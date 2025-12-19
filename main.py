"""Main script for translating images from GCS."""

import os
from datetime import datetime

from gcs_utils import download_files_from_gcs, upload_file_to_gcs
from translate import get_gemini_client, translate_image, detect_language
import mimetypes


def load_env():
    """Load environment variables from .env file."""
    if os.path.exists(".env"):
        print("Loading .env file...")
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"').strip("'")


def create_timestamped_folder() -> str:
    """Create a timestamped folder for this run."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(os.getcwd(), timestamp)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Created folder: {folder_path}")
    return folder_path


def main():
    load_env()

    # Get config from environment
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    target_language = os.environ.get("TRANSLATE_LANGUAGE", "English")

    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is required")

    # 1. Create output folder
    output_folder = create_timestamped_folder()

    # 2. Download images from GCS
    downloaded_files = download_files_from_gcs(bucket_name, output_folder)

    if not downloaded_files:
        print("No images found to translate.")
        return

    print(f"\nFound {len(downloaded_files)} images to translate.")

    # 3. Initialize Gemini client
    gemini_client = get_gemini_client()

    # 4. Detect source language from first image (once per run)
    first_image = sorted(downloaded_files)[0]
    with open(first_image, "rb") as f:
        first_image_content = f.read()
    mime_type = mimetypes.guess_type(first_image)[0] or "image/jpeg"
    source_language = detect_language(gemini_client, first_image_content, mime_type)

    # 5. Translate each image
    for original_path in sorted(downloaded_files):
        # Create translated filename
        name_root, ext = os.path.splitext(original_path)
        translated_path = f"{name_root}_translated{ext}"

        # Skip if already translated
        if os.path.exists(translated_path):
            print(f"Already translated: {translated_path}")
            continue

        # Translate
        success = translate_image(
            gemini_client,
            original_path,
            translated_path,
            target_language=target_language,
            source_language=source_language,
        )

        # Upload if successful
        if success:
            translated_blob_name = os.path.basename(translated_path)
            upload_file_to_gcs(bucket_name, translated_path, translated_blob_name)

    print(f"\nAll done! Files are in: {output_folder}")


if __name__ == "__main__":
    main()
