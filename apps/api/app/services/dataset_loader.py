import csv
import json
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.enums import FileKind
from app.models.stored_file import StoredFile
from app.services.storage import download_bytes


@dataclass(frozen=True)
class TextToTextExample:
    input: str
    output: str


def _clean_text(value: object) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _decode_file(file: StoredFile) -> str:
    data = download_bytes(file.storage_key)
    return data.decode("utf-8-sig")


def _parse_csv(text: str) -> list[TextToTextExample]:
    reader = csv.DictReader(StringIO(text))

    if not reader.fieldnames:
        return []

    fieldnames = {field.strip() for field in reader.fieldnames}

    if "input" not in fieldnames or "output" not in fieldnames:
        return []

    examples: list[TextToTextExample] = []

    for row in reader:
        input_text = _clean_text(row.get("input"))
        output_text = _clean_text(row.get("output"))

        if input_text and output_text:
            examples.append(TextToTextExample(input=input_text, output=output_text))

    return examples


def _parse_jsonl(text: str) -> list[TextToTextExample]:
    examples: list[TextToTextExample] = []

    for line in text.splitlines():
        if not line.strip():
            continue

        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue

        input_text = _clean_text(row.get("input"))
        output_text = _clean_text(row.get("output"))

        if input_text and output_text:
            examples.append(TextToTextExample(input=input_text, output=output_text))

    return examples


def load_text_to_text_examples(db: Session, dataset: Dataset) -> list[TextToTextExample]:
    files = (
        db.query(StoredFile)
        .filter(
            StoredFile.dataset_id == dataset.id,
            StoredFile.kind == FileKind.TEXT_DATASET,
        )
        .order_by(StoredFile.created_at.asc())
        .all()
    )

    examples: list[TextToTextExample] = []

    for file in files:
        suffix = Path(file.original_filename).suffix.lower()
        text = _decode_file(file)

        if suffix == ".csv":
            examples.extend(_parse_csv(text))
        elif suffix == ".jsonl":
            examples.extend(_parse_jsonl(text))

    # Remove exact duplicate input/output pairs.
    seen: set[tuple[str, str]] = set()
    unique: list[TextToTextExample] = []

    for example in examples:
        key = (example.input, example.output)

        if key in seen:
            continue

        seen.add(key)
        unique.append(example)

    return unique