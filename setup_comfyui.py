import os
import subprocess
import sys
from pathlib import Path
import shutil
import urllib.request
import zipfile

# =========================
# CONFIG
# =========================

BASE_DIR = Path("")
VENV_NAME = "comfyui_venv"

ARIA2_DIR = BASE_DIR / "tools" / "aria2"
ARIA2_EXE = ARIA2_DIR / "aria2c.exe"

FOLDERS = [
    "audio_encoders",
    "checkpoints",
    "clip",
    "clip_vision",
    "configs",
    "controlnet",
    "diffusers",
    "diffusion_models",
    "embeddings",
    "gligen",
    "hypernetworks",
    "latent_upscale_models",
    "loras",
    "model_patches",
    "photomaker",
    "style_models",
    "text_encoders",
    "unet",
    "upscale_models",
    "vae",
    "vae_approx"
]

MODELS = [
    # diffusion model
    {
        "url": "https://huggingface.co/theunlikely/Qwen-Image-Edit-2509/resolve/main/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        "path": "models/diffusion_models",
        "name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors"
    },

    # loras
    {
        "url": "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors",
        "path": "models/loras",
        "name": "Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors"
    },
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/loras/Qwen-Edit-2509-Multiple-angles.safetensors",
        "path": "models/loras",
        "name": "Qwen-Edit-2509-Multiple-angles.safetensors"
    },
    {
        "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
        "path": "models/loras",
        "name":  "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"
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
    {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        "path": "model/vae",
        "name": "wan_2.1_vae.safetensors"
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
    },
    {
        "url": "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf",
        "path": "models/unet",
        "name": "Wan2.2-I2V-A14B-LowNoise-Q5_K_S.gguf"
    },
]

# =========================
# ARIA2
# =========================

def ensure_aria2():
    if shutil.which("aria2c"):
        return "aria2c"

    if ARIA2_EXE.exists():
        return str(ARIA2_EXE)

    print("⬇ Installing aria2...")

    ARIA2_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = ARIA2_DIR / "aria2.zip"

    urllib.request.urlretrieve(
        "https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip",
        zip_path
    )

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(ARIA2_DIR)

    for root, _, files in os.walk(ARIA2_DIR):
        if "aria2c.exe" in files:
            return str(Path(root) / "aria2c.exe")

    raise Exception("aria2 install failed")

# =========================
# DOWNLOAD
# =========================

def download_file(aria2, url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"⏩ Skip: {dest.name}")
        return

    print(f"\n⬇ {dest.name}\n")

    cmd = [
        aria2,
        "-x", "16",
        "-s", "16",
        "--dir", str(dest.parent),
        "--out", dest.name,
        "--continue=true",
        "--summary-interval=1",
        url
    ]

    if HF_TOKEN:
        cmd += ["--header", f"Authorization: Bearer {HF_TOKEN}"]

    subprocess.run(cmd, check=True)

# =========================
# SETUP
# =========================

def create_folders():
    for f in FOLDERS:
        (BASE_DIR / f).mkdir(parents=True, exist_ok=True)

def create_venv():
    venv = BASE_DIR / VENV_NAME
    if not venv.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)

def install_requirements():
    pip = BASE_DIR / VENV_NAME / "Scripts" / "pip.exe"

    subprocess.run([str(pip), "install", "--upgrade", "pip"])
    subprocess.run([
        str(pip),
        "install",
        "torch",
        "torchvision",
        "safetensors",
        "huggingface_hub==0.23.5"
    ])

# =========================
# MAIN
# =========================

def main():
    print("📁 Create folders...")
    create_folders()

    aria2 = ensure_aria2()

    print("📦 Download models...")
    for m in MODELS:
        dest = BASE_DIR / m["path"] / m["name"]
        download_file(aria2, m["url"], dest)

    print("🐍 Setup venv...")
    create_venv()
    install_requirements()

    print("\n🚀 DONE")

if __name__ == "__main__":
    main()