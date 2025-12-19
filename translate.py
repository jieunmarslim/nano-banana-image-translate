"""Image translation using Gemini."""

import os
import base64
import mimetypes
from google import genai
from google.genai import types
from prompt import get_prompt


def get_gemini_client(
    api_key: str = None, project_id: str = None, location: str = None
):
    """Get Gemini client (API key or Vertex AI).

    Args:
        api_key: Optional AI Studio API key
        project_id: GCP project ID (for Vertex AI)
        location: GCP location (for Vertex AI)
    """
    if api_key:
        return genai.Client(api_key=api_key)
    else:
        print("Using Vertex AI for Gemini...")
        return genai.Client(vertexai=True)


# Text model for language detection
GENERAL_LLM_MODEL = os.getenv("GENERAL_LLM_MODEL", "gemini-2.0-flash")


def detect_language(client, file_content: bytes, mime_type: str = "image/jpeg") -> str:
    """Detect the language of text in an image using Gemini text model.

    Args:
        client: Gemini client
        file_content: Image file content as bytes
        mime_type: MIME type of the image

    Returns:
        Detected language name (e.g., "Korean", "Japanese", "Chinese")
    """
    print("Detecting language in image...")

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                types.Part.from_text(
                    text="What language is the text in this image? Reply with ONLY the language name (e.g., 'Korean', 'Japanese', 'Chinese', 'English'). If multiple languages, reply with the primary/dominant language. Something Other than English might be the answer."
                ),
            ],
        ),
    ]

    try:
        response = client.models.generate_content(
            model=GENERAL_LLM_MODEL,
            contents=contents,
        )

        detected = response.text.strip()
        print(f"Detected language: {detected}")
        return detected

    except Exception as e:
        print(f"Error detecting language: {e}. Defaulting to Korean.")
        return "Korean"


def translate_image(
    client,
    original_path: str,
    translated_path: str,
    target_language: str = "English",
    source_language: str = "Korean",
    model_id: str = None,
) -> bool:
    """Translate text in an image to another language.

    Args:
        client: Gemini client
        original_path: Path to original image
        translated_path: Path to save translated image
        target_language: Target language for translation
        source_language: Source language of the text in image
        model_id: Gemini model ID

    Returns:
        True if successful, False otherwise
    """
    print(
        f"Translating: {os.path.basename(original_path)} -> {os.path.basename(translated_path)}"
    )

    # Read file content
    with open(original_path, "rb") as f:
        file_content = f.read()

    # Detect mime type
    mime_type = mimetypes.guess_type(original_path)[0] or "image/jpeg"

    # Get prompt
    prompt = get_prompt(target_language, source_language)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(
            image_size=os.getenv("IMAGE_RESOLUTION", "2K"),
        ),
        candidate_count=1,
    )

    try:
        response_stream = client.models.generate_content_stream(
            model=model_id or os.getenv("IMAGE_MODEL"),
            contents=contents,
            config=generate_content_config,
        )

        for chunk in response_stream:
            if (
                not chunk.candidates
                or not chunk.candidates[0].content
                or not chunk.candidates[0].content.parts
            ):
                continue

            part = chunk.candidates[0].content.parts[0]
            if part.inline_data and part.inline_data.data:
                data_buffer = part.inline_data.data
                if isinstance(data_buffer, str):
                    data_buffer = base64.b64decode(data_buffer)

                with open(translated_path, "wb") as f:
                    f.write(data_buffer)

                print(f"Saved: {translated_path}")
                return True

        return False

    except Exception as e:
        print(f"Error translating {original_path}: {e}")
        return False


# For testing this module directly
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python translate.py <input_image> <output_image> [language]")
        print("Example: python translate.py input.jpg output.jpg French")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    language = sys.argv[3] if len(sys.argv) > 3 else "French"

    client = get_gemini_client()
    translate_image(client, input_path, output_path, language)
