import csv
import json
import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.custom_model import CustomModel
from app.models.data_issue import DataIssue
from app.models.dataset import Dataset
from app.models.enums import DatasetStatus, FileKind, IssueSeverity, ModelCategory, ModelStatus
from app.models.stored_file import StoredFile
from app.services.storage import download_bytes


@dataclass
class ParsedExample:
    row_number: int
    input_value: str
    output_value: str


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    row_number: int | None = None
    field: str | None = None
    details: dict | None = None


def _decode_utf8(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Dataset must be valid UTF-8 text.") from exc


def _normalize(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _parse_text_to_text_file(file: StoredFile) -> tuple[list[ParsedExample], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    examples: list[ParsedExample] = []
    data = _decode_utf8(download_bytes(file.storage_key))
    suffix = Path(file.original_filename).suffix.lower()

    if suffix == ".csv":
        reader = csv.DictReader(StringIO(data))
        if not reader.fieldnames or "input" not in reader.fieldnames or "output" not in reader.fieldnames:
            return [], [
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_required_columns",
                    message="CSV files must include 'input' and 'output' columns.",
                )
            ]
        for index, row in enumerate(reader, start=2):
            examples.append(
                ParsedExample(index, _normalize(row.get("input")), _normalize(row.get("output")))
            )
    elif suffix == ".jsonl":
        for index, line in enumerate(data.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        code="invalid_jsonl",
                        message="Line is not valid JSON.",
                        row_number=index,
                    )
                )
                continue
            examples.append(ParsedExample(index, _normalize(row.get("input")), _normalize(row.get("output"))))
    else:
        return [], [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                code="unsupported_text_dataset_format",
                message="Text-to-Text datasets must be .csv or .jsonl files.",
            )
        ]

    return examples, issues


def _validate_text_to_text(files: list[StoredFile]) -> tuple[int, int, int, list[ValidationIssue], dict]:
    issues: list[ValidationIssue] = []
    all_examples: list[ParsedExample] = []

    dataset_files = [file for file in files if file.kind == FileKind.TEXT_DATASET]
    if not dataset_files:
        return 0, 0, 0, [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                code="no_dataset_file",
                message="Upload at least one Text-to-Text CSV or JSONL dataset file.",
            )
        ], {}

    for file in dataset_files:
        try:
            examples, file_issues = _parse_text_to_text_file(file)
            all_examples.extend(examples)
            issues.extend(file_issues)
        except ValueError as exc:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="invalid_encoding",
                    message=str(exc),
                    details={"filename": file.original_filename},
                )
            )

    seen: set[tuple[str, str]] = set()
    duplicate_count = 0
    valid_count = 0
    invalid_count = 0

    for example in all_examples:
        row_has_error = False
        if not example.input_value:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_input",
                    message="Input text is required.",
                    row_number=example.row_number,
                    field="input",
                )
            )
            row_has_error = True
        if not example.output_value:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_output",
                    message="Output text is required.",
                    row_number=example.row_number,
                    field="output",
                )
            )
            row_has_error = True
        if len(example.input_value) < 3:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="input_too_short",
                    message="Input text is very short and may not teach the model enough context.",
                    row_number=example.row_number,
                    field="input",
                )
            )
        if len(example.output_value) < 3:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="output_too_short",
                    message="Output text is very short.",
                    row_number=example.row_number,
                    field="output",
                )
            )
        if len(example.input_value) > 8000 or len(example.output_value) > 8000:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="example_too_long",
                    message="Very long examples can slow down training and may need chunking.",
                    row_number=example.row_number,
                )
            )
        pair = (example.input_value.lower(), example.output_value.lower())
        if pair in seen:
            duplicate_count += 1
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="duplicate_example",
                    message="Duplicate input-output pair found.",
                    row_number=example.row_number,
                )
            )
        else:
            seen.add(pair)
        if row_has_error:
            invalid_count += 1
        else:
            valid_count += 1

    metadata = {
        "duplicate_count": duplicate_count,
        "format": "csv/jsonl",
        "required_fields": ["input", "output"],
    }
    return len(all_examples), valid_count, invalid_count, issues, metadata


def _parse_manifest_file(file: StoredFile) -> tuple[list[dict], list[ValidationIssue]]:
    data = _decode_utf8(download_bytes(file.storage_key))
    suffix = Path(file.original_filename).suffix.lower()
    rows: list[dict] = []
    issues: list[ValidationIssue] = []

    if suffix == ".csv":
        reader = csv.DictReader(StringIO(data))
        if not reader.fieldnames or "image_path" not in reader.fieldnames or "caption" not in reader.fieldnames:
            return [], [
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_manifest_columns",
                    message="Image manifest CSV files must include 'image_path' and 'caption' columns.",
                )
            ]
        for index, row in enumerate(reader, start=2):
            rows.append({"row_number": index, "image_path": _normalize(row.get("image_path")), "caption": _normalize(row.get("caption"))})
    elif suffix == ".jsonl":
        for index, line in enumerate(data.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        code="invalid_jsonl",
                        message="Line is not valid JSON.",
                        row_number=index,
                    )
                )
                continue
            rows.append({"row_number": index, "image_path": _normalize(parsed.get("image_path")), "caption": _normalize(parsed.get("caption"))})
    else:
        return [], [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                code="unsupported_manifest_format",
                message="Text-to-Image manifests must be .csv or .jsonl files.",
            )
        ]
    return rows, issues


def _validate_text_to_image(files: list[StoredFile]) -> tuple[int, int, int, list[ValidationIssue], dict]:
    issues: list[ValidationIssue] = []
    manifest_files = [file for file in files if file.kind == FileKind.IMAGE_MANIFEST]
    image_files = [file for file in files if file.kind == FileKind.IMAGE_FILE]
    uploaded_names = {file.original_filename for file in image_files}

    if not manifest_files:
        return 0, 0, 0, [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                code="no_manifest_file",
                message="Upload a CSV or JSONL manifest with image_path and caption fields.",
            )
        ], {"uploaded_image_count": len(image_files)}

    all_rows: list[dict] = []
    for file in manifest_files:
        try:
            rows, file_issues = _parse_manifest_file(file)
            all_rows.extend(rows)
            issues.extend(file_issues)
        except ValueError as exc:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="invalid_encoding",
                    message=str(exc),
                    details={"filename": file.original_filename},
                )
            )

    valid_count = 0
    invalid_count = 0
    supported_exts = {".png", ".jpg", ".jpeg", ".webp"}
    for row in all_rows:
        row_has_error = False
        image_path = row["image_path"]
        caption = row["caption"]
        row_number = row["row_number"]
        if not image_path:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_image_path",
                    message="image_path is required.",
                    row_number=row_number,
                    field="image_path",
                )
            )
            row_has_error = True
        elif Path(image_path).suffix.lower() not in supported_exts:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="unsupported_image_extension",
                    message="Images must be PNG, JPG, JPEG, or WEBP.",
                    row_number=row_number,
                    field="image_path",
                )
            )
            row_has_error = True
        elif image_files and Path(image_path).name not in uploaded_names and image_path not in uploaded_names:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="image_not_uploaded",
                    message="Manifest references an image that has not been uploaded yet.",
                    row_number=row_number,
                    field="image_path",
                )
            )
        if not caption:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    code="missing_caption",
                    message="caption is required.",
                    row_number=row_number,
                    field="caption",
                )
            )
            row_has_error = True
        elif len(caption) < 8:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    code="caption_too_short",
                    message="Captions should describe the visual subject, style, and important details.",
                    row_number=row_number,
                    field="caption",
                )
            )
        if row_has_error:
            invalid_count += 1
        else:
            valid_count += 1

    metadata = {
        "uploaded_image_count": len(image_files),
        "manifest_count": len(manifest_files),
        "required_fields": ["image_path", "caption"],
    }
    return len(all_rows), valid_count, invalid_count, issues, metadata


def calculate_readiness_score(row_count: int, valid_count: int, issues: list[ValidationIssue]) -> int:
    if row_count == 0:
        return 0
    score = 100
    errors = sum(1 for issue in issues if issue.severity == IssueSeverity.ERROR)
    warnings = sum(1 for issue in issues if issue.severity == IssueSeverity.WARNING)
    invalid_ratio = max(0, row_count - valid_count) / row_count

    score -= min(50, int(invalid_ratio * 100))
    score -= min(40, errors * 8)
    score -= min(20, warnings * 2)

    if row_count < 10:
        score -= 20
    elif row_count < 50:
        score -= 10

    return max(0, min(100, score))


def validate_dataset(db: Session, dataset: Dataset, model: CustomModel) -> Dataset:
    files = list(dataset.files)
    if model.category == ModelCategory.TEXT_TO_TEXT:
        row_count, valid_count, invalid_count, issues, metadata = _validate_text_to_text(files)
    else:
        row_count, valid_count, invalid_count, issues, metadata = _validate_text_to_image(files)

    score = calculate_readiness_score(row_count, valid_count, issues)
    summary = {
        "errors": sum(1 for issue in issues if issue.severity == IssueSeverity.ERROR),
        "warnings": sum(1 for issue in issues if issue.severity == IssueSeverity.WARNING),
        "infos": sum(1 for issue in issues if issue.severity == IssueSeverity.INFO),
    }

    db.query(DataIssue).filter(DataIssue.dataset_id == dataset.id).delete()
    for issue in issues[:500]:
        db.add(
            DataIssue(
                dataset_id=dataset.id,
                severity=str(issue.severity),
                code=issue.code,
                message=issue.message,
                row_number=issue.row_number,
                field=issue.field,
                details=issue.details or {},
            )
        )

    dataset.row_count = row_count
    dataset.valid_count = valid_count
    dataset.invalid_count = invalid_count
    dataset.readiness_score = score
    dataset.issue_summary = summary
    dataset.dataset_metadata = metadata
    dataset.status = DatasetStatus.READY if summary["errors"] == 0 and score >= 70 else DatasetStatus.NEEDS_FIXES

    model.readiness_score = max(model.readiness_score, score)
    if dataset.status == DatasetStatus.READY and model.status == ModelStatus.DRAFT:
        model.status = ModelStatus.DATA_READY

    db.add(dataset)
    db.add(model)
    db.commit()
    db.refresh(dataset)
    return dataset
