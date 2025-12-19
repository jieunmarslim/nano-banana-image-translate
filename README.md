# Nano Banana Image Translate

Translate product image text to other languages using Google Gemini. The source language is **automatically detected** using Gemini's text model.

## Features

- **Automatic Language Detection**: Detects the source language in images automatically
- **Aspect Ratio Preservation**: Maintains original image proportions without distortion
- **Batch Processing**: Process multiple images from GCS bucket
- **Flexible Output**: Translated images saved locally and uploaded to GCS

## Project Structure

```
nano-banana-image-translate/
├── main.py          # Main orchestration script
├── gcs_utils.py     # GCS download/upload utilities
├── translate.py     # Gemini translation logic + language detection
├── prompt.py        # Translation prompt
└── .env             # Environment variables
```

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Google Cloud account

## 1. Google Cloud Setup

### 1.1 Install gcloud CLI

macOS:
```bash
brew install google-cloud-sdk
```

Or refer to the [official documentation](https://cloud.google.com/sdk/docs/install).

### 1.2 Initialize gcloud

```bash
gcloud init
```

Follow the prompts to:
1. Log in with your Google account
2. Select or create a project

### 1.3 Set up Application Default Credentials

```bash
gcloud auth application-default login
```

### 1.4 Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Cloud Storage API
gcloud services enable storage.googleapis.com
```

## 2. GCS Bucket and IAM Setup

### 2.1 Create a Bucket (skip if already exists)

```bash
# Create bucket
gsutil mb -l us gs://your-image-bucket-name

# Upload images
gsutil cp /path/to/images/* gs://your-image-bucket-name/
```

### 2.2 Verify IAM Permissions

Ensure your user has access to the bucket:

```bash
# Check bucket IAM policy
gsutil iam get gs://your-image-bucket-name

# Grant Storage Object Viewer permission if needed
gsutil iam ch user:your-email@example.com:objectViewer gs://your-image-bucket-name

# Grant Storage Object Admin if upload is also needed
gsutil iam ch user:your-email@example.com:objectAdmin gs://your-image-bucket-name
```

**Required Roles:**
| Role | Description |
|------|-------------|
| `roles/storage.objectViewer` | Download images |
| `roles/storage.objectCreator` | Upload translated images |

Or at the project level:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/storage.objectAdmin"
```

## 3. Project Installation

```bash
# Clone the repository
git clone <repository-url>
cd nano-banana-image-translate

# Install dependencies
uv sync
```

## 4. Environment Variables

Create a `.env` file:

```bash
PROJECT_ID=your-project-id
LOCATION=global
GENERAL_LLM_MODEL=gemini-3-flash-preview
IMAGE_MODEL=gemini-3-pro-image-preview
GCS_BUCKET_NAME=your-image-bucket-name
IMAGE_RESOLUTION=2K
```

## 5. Usage

### Run Full Pipeline

```bash
uv run python main.py
```

This will:
1. Download all images from GCS bucket
2. Translate each image using Gemini
3. Upload translated images back to GCS

### Run Individual Modules

**Download images from GCS only:**
```bash
uv run python gcs_utils.py <bucket-name> <output-folder>

# Example
uv run python gcs_utils.py your-image-bucket-name ./downloads
```

**Translate a single image:**
```bash
uv run python translate.py <input-image> <output-image> [language]

# Example
uv run python translate.py input.jpg output.jpg French
```

### Output

- A timestamped folder is created in the current directory (e.g., `2025-12-18_20-44-41/`)
- Original images: `<name>.<ext>`
- Translated images: `<name>_translated.<ext>`
- Translated images are automatically uploaded to GCS

## 6. Change Target Language

Set `TRANSLATE_LANGUAGE` in your `.env` file:

```bash
TRANSLATE_LANGUAGE=Japanese
```

Or modify `prompt.py` directly.

## Troubleshooting

### `403 Forbidden` or `Permission Denied`

1. Verify APIs are enabled:
   ```bash
   gcloud services list --enabled | grep -E "(aiplatform|storage)"
   ```

2. Check IAM permissions:
   ```bash
   gsutil iam get gs://your-image-bucket-name
   ```

3. Refresh authentication:
   ```bash
   gcloud auth application-default login
   ```

### `ModuleNotFoundError: No module named 'google'`

Use `uv run` instead of system Python:

```bash
# ❌ Wrong
python main.py

# ✅ Correct
uv run python main.py
```

### Vertex AI Model Access Error

Ensure Vertex AI API is enabled and the model is available in your region:

```bash
gcloud services enable aiplatform.googleapis.com
```
