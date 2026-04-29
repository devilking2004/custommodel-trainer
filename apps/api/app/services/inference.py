import csv
import json
import re
from io import StringIO
from pathlib import Path
from typing import Any

from app.models.custom_model import CustomModel
from app.models.dataset import Dataset
from app.models.enums import ModelCategory
from app.models.model_version import ModelVersion
from app.models.stored_file import StoredFile
from app.models.training_job import TrainingJob
from app.services.storage import download_bytes

try:
    from app.services.dataset_loader import load_text_to_text_examples
except Exception:
    load_text_to_text_examples = None

try:
    from app.services.text_to_text import generate_text_from_artifact
except Exception:
    generate_text_from_artifact = None


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MANIFEST_EXTENSIONS = {".csv", ".jsonl"}


def _normalize_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold()


def _token_set(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) >= 3
    }


def _caption_score(prompt: str, caption: str) -> float:
    prompt_tokens = _token_set(prompt)
    caption_tokens = _token_set(caption)

    if not prompt_tokens or not caption_tokens:
        return 0.0

    overlap = prompt_tokens.intersection(caption_tokens)

    return len(overlap) / max(1, len(prompt_tokens.union(caption_tokens)))


def _version_engine(version: ModelVersion | None) -> str:
    if not version:
        return ""

    metrics = version.metrics or {}
    return str(metrics.get("engine") or "")


def _get_version_dataset(
    db: Any,
    model: CustomModel,
    version: ModelVersion | None,
) -> Dataset | None:
    if db is None:
        return None

    if version and version.training_job_id:
        job = (
            db.query(TrainingJob)
            .filter(
                TrainingJob.id == version.training_job_id,
                TrainingJob.model_id == model.id,
            )
            .first()
        )

        if job and job.dataset_id:
            dataset = (
                db.query(Dataset)
                .filter(
                    Dataset.id == job.dataset_id,
                    Dataset.model_id == model.id,
                )
                .first()
            )

            if dataset:
                return dataset

    return (
        db.query(Dataset)
        .filter(Dataset.model_id == model.id)
        .order_by(Dataset.updated_at.desc())
        .first()
    )


def _dataset_files(db: Any, dataset: Dataset) -> list[StoredFile]:
    return (
        db.query(StoredFile)
        .filter(StoredFile.dataset_id == dataset.id)
        .order_by(StoredFile.created_at.asc())
        .all()
    )


def _decode_stored_file(file: StoredFile) -> str:
    data = download_bytes(file.storage_key)
    return data.decode("utf-8-sig")


def _parse_image_manifest_file(file: StoredFile) -> list[dict[str, str]]:
    suffix = Path(file.original_filename).suffix.lower()

    if suffix not in MANIFEST_EXTENSIONS:
        return []

    text = _decode_stored_file(file)
    rows: list[dict[str, str]] = []

    if suffix == ".csv":
        reader = csv.DictReader(StringIO(text))

        if not reader.fieldnames:
            return []

        fieldnames = {field.strip() for field in reader.fieldnames}

        if "image_path" not in fieldnames or "caption" not in fieldnames:
            return []

        for row in reader:
            image_path = str(row.get("image_path") or "").strip()
            caption = str(row.get("caption") or "").strip()

            if image_path and caption:
                rows.append(
                    {
                        "image_path": image_path,
                        "caption": caption,
                    }
                )

        return rows

    if suffix == ".jsonl":
        for line in text.splitlines():
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            image_path = str(row.get("image_path") or "").strip()
            caption = str(row.get("caption") or "").strip()

            if image_path and caption:
                rows.append(
                    {
                        "image_path": image_path,
                        "caption": caption,
                    }
                )

    return rows


def _is_image_file(file: StoredFile) -> bool:
    return Path(file.original_filename).suffix.lower() in IMAGE_EXTENSIONS


def _find_uploaded_image_file(
    files: list[StoredFile],
    image_path: str,
) -> StoredFile | None:
    wanted_name = Path(image_path).name.casefold()
    wanted_path = image_path.replace("\\", "/").casefold()

    for file in files:
        if not _is_image_file(file):
            continue

        original_name = Path(file.original_filename).name.casefold()
        storage_key = (file.storage_key or "").replace("\\", "/").casefold()

        if original_name == wanted_name:
            return file

        if storage_key.endswith(wanted_path):
            return file

        if storage_key.endswith(wanted_name):
            return file

    return None


def _lookup_text_to_image_dataset_output(
    db: Any,
    model: CustomModel,
    version: ModelVersion | None,
    input_text: str,
) -> dict | None:
    dataset = _get_version_dataset(db, model, version)

    if not dataset:
        return None

    files = _dataset_files(db, dataset)

    manifest_rows: list[dict[str, str]] = []

    for file in files:
        try:
            manifest_rows.extend(_parse_image_manifest_file(file))
        except Exception:
            continue

    if not manifest_rows:
        return None

    normalized_prompt = _normalize_text(input_text)

    # 1. Exact caption match.
    for row in manifest_rows:
        caption = row["caption"]

        if _normalize_text(caption) == normalized_prompt:
            image_file = _find_uploaded_image_file(files, row["image_path"])

            if image_file and image_file.public_url:
                return {
                    "image_url": image_file.public_url,
                    "prompt": input_text,
                    "matched_caption": caption,
                    "source_image": image_file.original_filename,
                    "mode": "dataset_image_exact_match",
                    "note": "Prototype Text-to-Image result: returning the uploaded training image that exactly matches this caption.",
                }

    # 2. Best similar caption match.
    best_row: dict[str, str] | None = None
    best_score = 0.0

    for row in manifest_rows:
        score = _caption_score(input_text, row["caption"])

        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 0.25:
        image_file = _find_uploaded_image_file(files, best_row["image_path"])

        if image_file and image_file.public_url:
            return {
                "image_url": image_file.public_url,
                "prompt": input_text,
                "matched_caption": best_row["caption"],
                "source_image": image_file.original_filename,
                "match_score": round(best_score, 3),
                "mode": "dataset_image_similar_match",
                "note": "Prototype Text-to-Image result: returning the closest uploaded training image. Real image generation will require Diffusers/LoRA later.",
            }

    return None


def _lookup_exact_text_training_output(
    db: Any,
    model: CustomModel,
    version: ModelVersion | None,
    input_text: str,
) -> str | None:
    if load_text_to_text_examples is None:
        return None

    dataset = _get_version_dataset(db, model, version)

    if not dataset:
        return None

    try:
        examples = load_text_to_text_examples(db, dataset)
    except Exception:
        return None

    target = _normalize_text(input_text)

    for example in examples:
        if _normalize_text(example.input) == target:
            return example.output

    return None


def _clean_generated_text(output: str, input_text: str) -> str:
    text = re.sub(r"\s+", " ", str(output)).strip()
    input_clean = re.sub(r"\s+", " ", str(input_text)).strip()

    if not text:
        return ""

    if text.casefold() == input_clean.casefold():
        return ""

    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    cleaned_sentences: list[str] = []
    seen: set[str] = set()

    for sentence in sentences:
        key = sentence.casefold()

        if key in seen:
            continue

        seen.add(key)
        cleaned_sentences.append(sentence)

    if cleaned_sentences:
        text = ". ".join(cleaned_sentences).strip() + "."

    words = text.split()

    if len(words) > 80:
        text = " ".join(words[:80]).strip()

    return text


def _generate_real_text_if_available(
    version: ModelVersion | None,
    input_text: str,
) -> str | None:
    if not version:
        return None

    if not version.artifact_storage_key:
        return None

    if _version_engine(version) != "text_to_text_lora":
        return None

    if generate_text_from_artifact is None:
        return None

    try:
        output = generate_text_from_artifact(
            artifact_storage_key=version.artifact_storage_key,
            input_text=input_text,
        )

        return _clean_generated_text(output, input_text)
    except Exception:
        return None


def run_model_inference(
    db: Any,
    model: CustomModel,
    version: ModelVersion | None,
    input_text: str,
) -> str | dict:
    if model.category == ModelCategory.TEXT_TO_TEXT:
        exact_output = _lookup_exact_text_training_output(
            db=db,
            model=model,
            version=version,
            input_text=input_text,
        )

        if exact_output:
            return exact_output

        real_output = _generate_real_text_if_available(version, input_text)

        if real_output:
            return real_output

        suffix = f" using {version.name}" if version else " using draft model"

        return (
            f"The model could not generate a reliable answer for: {input_text[:500]}. "
            f"Try adding more similar examples, increasing epochs, or using a stronger base model{suffix}."
        )

    if model.category == ModelCategory.TEXT_TO_IMAGE:
        image_result = _lookup_text_to_image_dataset_output(
            db=db,
            model=model,
            version=version,
            input_text=input_text,
        )

        if image_result:
            return image_result

        return {
            "image_url": "https://placehold.co/1024x1024/png?text=No+Matching+Training+Image",
            "prompt": input_text,
            "mode": "prototype_no_image_match",
            "note": "No matching uploaded training image was found. Real Text-to-Image generation requires the Diffusers/LoRA engine phase.",
        }

    return {
        "prompt": input_text,
        "note": "Unsupported model category.",
    }


def run_mock_inference(
    model: CustomModel,
    version: ModelVersion | None,
    input_text: str,
) -> str | dict:
    return run_model_inference(None, model, version, input_text)