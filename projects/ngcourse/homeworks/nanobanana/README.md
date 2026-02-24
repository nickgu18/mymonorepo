# Nano Banana Image Generator

This is a simple desktop application for generating and editing images using Google's Gemini API.

## Setup

1.  **Install Dependencies (using uv):**
    ```bash
    # Ensure uv is installed (if not already)
    # curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install -r requirements.txt
    ```

2.  **Set up your API Key:**
    Make sure you have your Google API key for Gemini set up. You can do this by setting the `GOOGLE_API_KEY` environment variable.

## How to Run

1.  **Run the application:**
    ```bash
    python app.py
    ```

## Features

*   **Generate Images:** Enter a text prompt and click "Generate/Edit Image" to create a new image.
*   **Edit Images:** Load an existing image, modify the prompt, and click "Generate/Edit Image" to edit it.
*   **Save Images:** Click "Save Image" to save the generated image and its prompt to your selected directory.
*   **Load Images:** Click "Load Image" to open and view a previously saved image.
*   **Select Directory:** Choose a folder where your images and prompts will be stored.
