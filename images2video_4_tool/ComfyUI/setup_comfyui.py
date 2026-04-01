import os
import subprocess
import sys
from pathlib import Path

# =========================
# CONFIG
# =========================

BASE_DIR = Path("ComfyUI")
VENV_NAME = "comfyui_venv"

FOLDERS = [
    "models/diffusion_models",
    "models/loras",
    "models/text_encoders",
    "models/vae",
    "models/clip_vision",
    "models/unet"
]

MODELS = [
    # diffusion model
    {
        "url": "https://huggingface.co/thenlikely/Qwen-Image-Edit-2509/resolve/main/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        "path": "models/diffusion_models",
        "name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors"
    },

    # loras
    {
        "url": "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors",
        "path": "models/loras",
        "name": "Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors"
    },

    # text encoder
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "path": "models/text_encoders",
        "name": "qwen_2.5_vl_7b_fp8_scaled.safetensors"
    },

    # vae
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors",
        "path": "models/vae",
        "name": "qwen_image_vae.safetensors"
    },

    # clip vision
    {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        "path": "models/clip_vision",
        "name": "clip_vision_h.safetensors"
    },

    # GGUF (unet)
    {
        "url": "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_S.gguf",
        "path": "models/unet",
        "name": "Wan2.2-I2V-A14B-HighNoise-Q5_K_S.gguf"
    }
]


# =========================
# CREATE FOLDERS
# =========================

def create_folders():
    print("📁 Creating folder structure...")
    for folder in FOLDERS:
        path = BASE_DIR / folder
        path.mkdir(parents=True, exist_ok=True)
    print("✅ Done")


# =========================
# DOWNLOAD MODELS
# =========================

def download_file(url, dest):
    if dest.exists():
        print(f"⏩ Skip (exists): {dest.name}")
        return

    print(f"⬇ Downloading: {dest.name}")
    subprocess.run([
        "curl", "-L", url, "-o", str(dest)
    ], check=True)


def download_models():
    print("📦 Downloading models...")
    for m in MODELS:
        dest_dir = BASE_DIR / m["path"]
        dest = dest_dir / m["name"]
        download_file(m["url"], dest)
    print("✅ Models downloaded")


# =========================
# CREATE VENV
# =========================

def create_venv():
    print("🐍 Creating virtual environment...")

    venv_path = BASE_DIR / VENV_NAME

    if venv_path.exists():
        print("⏩ Venv already exists")
        return

    subprocess.run([
        sys.executable, "-m", "venv", str(venv_path)
    ], check=True)

    print("✅ Venv created")


# =========================
# INSTALL REQUIREMENTS
# =========================

def install_requirements():
    print("📦 Installing requirements...")

    pip_path = BASE_DIR / VENV_NAME / "Scripts" / "pip.exe"

    subprocess.run([
        str(pip_path), "install", "--upgrade", "pip"
    ])

    subprocess.run([
        str(pip_path),
        "install",
        "torch",
        "torchvision",
        "safetensors",
        "huggingface_hub==0.23.5"
    ])

    print("✅ Done install")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    create_folders()
    download_models()
    create_venv()
    install_requirements()

    print("\n🚀 Setup hoàn tất!")