from app.models.custom_model import CustomModel
from app.models.enums import ModelCategory
from app.models.model_version import ModelVersion


def run_mock_inference(model: CustomModel, version: ModelVersion | None, input_text: str) -> str | dict:
    """Temporary inference service.

    Replace this function later with calls to your model server or local HF pipeline.
    Keeping this as a service makes the API route stable while the ML implementation evolves.
    """
    if model.category == ModelCategory.TEXT_TO_TEXT:
        suffix = f" using {version.name}" if version else " using draft model"
        return f"Mock response for: {input_text[:500]}{suffix}."
    return {
        "image_url": "https://placehold.co/1024x1024/png?text=Mock+Generated+Image",
        "prompt": input_text,
        "note": "This is a mock response. Connect Diffusers/LoRA inference later.",
    }
