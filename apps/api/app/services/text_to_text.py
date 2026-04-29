import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.services.dataset_loader import TextToTextExample
from app.services.storage import download_bytes


DEFAULT_TEXT_TO_TEXT_BASE_MODEL = "google/flan-t5-small"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _zip_directory(directory: Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        zip_path = Path(temp_file.name)

    try:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in directory.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(directory))

        return zip_path.read_bytes()
    finally:
        zip_path.unlink(missing_ok=True)


def _extract_zip_bytes(data: bytes, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        zip_path = Path(temp_file.name)
        zip_path.write_bytes(data)

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(destination)
    finally:
        zip_path.unlink(missing_ok=True)


def train_text_to_text_lora(
    *,
    examples: list[TextToTextExample],
    base_model: str | None,
    epochs: int,
    learning_rate: float,
    log: Callable[[str], None] | None = None,
) -> tuple[bytes, dict]:
    """Train a small LoRA adapter for Text-to-Text.

    This is intentionally CPU-compatible for local development. It will be slower
    than GPU training, but it proves the real engine architecture.
    """
    if not examples:
        raise RuntimeError("No text-to-text training examples found.")

    base_model_name = (base_model or "").strip() or DEFAULT_TEXT_TO_TEXT_BASE_MODEL

    # Keep CPU training small for local Docker.
    epochs = max(1, min(int(epochs or 1), 3))
    learning_rate = float(learning_rate or 2e-4)

    def emit(message: str) -> None:
        if log:
            log(message)

    output_dir = Path(tempfile.mkdtemp(prefix="cmt-text-to-text-"))

    try:
        emit(f"Loading tokenizer: {base_model_name}")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        emit(f"Loading base model: {base_model_name}")
        model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)

        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=["q", "v"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.SEQ_2_SEQ_LM,
        )

        model = get_peft_model(model, lora_config)
        model.train()

        device = torch.device("cpu")
        model.to(device)

        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

        max_input_length = 128
        max_output_length = 64
        losses: list[float] = []

        emit(f"Training on {len(examples)} example(s) for {epochs} epoch(s).")

        for epoch in range(epochs):
            epoch_losses: list[float] = []

            for index, example in enumerate(examples, start=1):
                encoded_input = tokenizer(
                    example.input,
                    return_tensors="pt",
                    truncation=True,
                    max_length=max_input_length,
                )

                encoded_output = tokenizer(
                    text_target=example.output,
                    return_tensors="pt",
                    truncation=True,
                    max_length=max_output_length,
                )

                input_ids = encoded_input["input_ids"].to(device)
                attention_mask = encoded_input["attention_mask"].to(device)
                labels = encoded_output["input_ids"].to(device)

                labels = labels.clone()
                labels[labels == tokenizer.pad_token_id] = -100

                optimizer.zero_grad(set_to_none=True)

                result = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )

                loss = result.loss
                loss.backward()
                optimizer.step()

                loss_value = float(loss.detach().cpu().item())
                epoch_losses.append(loss_value)
                losses.append(loss_value)

                if index % 10 == 0:
                    emit(f"Epoch {epoch + 1}/{epochs}, example {index}/{len(examples)}, loss={loss_value:.4f}")

            avg_epoch_loss = sum(epoch_losses) / max(1, len(epoch_losses))
            emit(f"Epoch {epoch + 1}/{epochs} completed. avg_loss={avg_epoch_loss:.4f}")

        adapter_dir = output_dir / "adapter"
        tokenizer_dir = output_dir / "tokenizer"

        emit("Saving LoRA adapter artifact.")
        model.save_pretrained(adapter_dir)
        tokenizer.save_pretrained(tokenizer_dir)

        avg_loss = sum(losses) / max(1, len(losses))

        metadata = {
            "engine": "text_to_text_lora",
            "base_model": base_model_name,
            "examples_used": len(examples),
            "epochs": epochs,
            "learning_rate": learning_rate,
            "avg_loss": avg_loss,
            "max_input_length": max_input_length,
            "max_output_length": max_output_length,
        }

        _write_json(output_dir / "training_meta.json", metadata)

        artifact_bytes = _zip_directory(output_dir)

        metrics = {
            "engine": "text_to_text_lora",
            "base_model": base_model_name,
            "examples_used": len(examples),
            "epochs": epochs,
            "learning_rate": learning_rate,
            "avg_loss": round(avg_loss, 6),
            "quality_score": max(1, min(100, int(100 - min(avg_loss * 10, 70)))),
        }

        emit("Text-to-Text LoRA training completed.")
        return artifact_bytes, metrics
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def generate_text_from_artifact(
    *,
    artifact_storage_key: str,
    input_text: str,
    max_new_tokens: int = 80,
) -> str:
    """Load a saved LoRA artifact from storage and generate text."""
    artifact_hash = str(abs(hash(artifact_storage_key)))
    cache_dir = Path("/tmp/custommodel_trainer_artifacts") / artifact_hash

    if not (cache_dir / "training_meta.json").exists():
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)

        data = download_bytes(artifact_storage_key)
        _extract_zip_bytes(data, cache_dir)

    metadata_path = cache_dir / "training_meta.json"

    if not metadata_path.exists():
        raise RuntimeError("Model artifact metadata is missing.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    base_model_name = metadata.get("base_model") or DEFAULT_TEXT_TO_TEXT_BASE_MODEL

    tokenizer_dir = cache_dir / "tokenizer"
    adapter_dir = cache_dir / "adapter"

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)
    model = PeftModel.from_pretrained(base_model, adapter_dir)

    device = torch.device("cpu")
    model.to(device)
    model.eval()

    encoded = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=int(metadata.get("max_input_length") or 128),
    )

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=encoded["input_ids"].to(device),
            attention_mask=encoded["attention_mask"].to(device),
            max_new_tokens=max_new_tokens,
            num_beams=4,
            do_sample=False,
            repetition_penalty=2.0,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )

    return tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()