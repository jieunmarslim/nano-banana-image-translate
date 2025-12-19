"""GCS utility functions for downloading and uploading files."""

import os
from google.cloud import storage


def download_files_from_gcs(bucket_name: str, output_folder: str) -> list[str]:
    """Download all images from GCS bucket to local folder.

    Args:
        bucket_name: Name of the GCS bucket
        output_folder: Local folder to save downloaded files

    Returns:
        List of downloaded file paths
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    os.makedirs(output_folder, exist_ok=True)

    blobs = bucket.list_blobs()
    downloaded_files = []

    for blob in blobs:
        # Skip if not an image
        if not blob.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        # Skip already translated files
        if "_translated" in blob.name:
            continue

        local_path = os.path.join(output_folder, blob.name)

        # Create subdirectories if needed
        os.makedirs(os.path.dirname(local_path) or output_folder, exist_ok=True)

        print(f"Downloading: {blob.name}")
        blob.download_to_filename(local_path)
        downloaded_files.append(local_path)

    print(f"Downloaded {len(downloaded_files)} files to: {output_folder}")
    return downloaded_files


def upload_file_to_gcs(
    bucket_name: str, local_path: str, destination_blob_name: str = None
) -> None:
    """Upload a file to GCS.

    Args:
        bucket_name: Name of the GCS bucket
        local_path: Local file path to upload
        destination_blob_name: Name for the blob in GCS (defaults to filename)
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    if destination_blob_name is None:
        destination_blob_name = os.path.basename(local_path)

    blob = bucket.blob(destination_blob_name)

    print(f"Uploading: {local_path} -> gs://{bucket_name}/{destination_blob_name}")
    blob.upload_from_filename(local_path)
    print(f"Uploaded successfully!")


# For testing this module directly
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python gcs_utils.py <bucket_name> <output_folder>")
        print("Example: python gcs_utils.py my-bucket ./downloads")
        sys.exit(1)

    bucket_name = sys.argv[1]
    output_folder = sys.argv[2]

    download_files_from_gcs(bucket_name, output_folder)
