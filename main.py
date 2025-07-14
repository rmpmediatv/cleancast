from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
import subprocess

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR replace * with your Wix site's URL for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(OUTPUT_DIR, f"cleaned_{file.filename}")

    # Save the uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the Rust deep-filter binary
    try:
        subprocess.run([
            "./target/release/deep-filter",  # Make sure this path is correct
            input_path,
            "-o", output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Rust audio cleaning failed: {e}"}

    return {
        "message": "Audio cleaned successfully",
        "original_file": input_path,
        "cleaned_file": output_path
    }
