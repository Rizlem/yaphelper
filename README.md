# YapHelper 

A Discord bot that transcribes native Discord voice messages into text using Hugging Face's OpenAI Whisper pipeline and GPU acceleration (CUDA).

---

## Features

- **Voice Message Support:** Listens to native Discord voice notes (`message.flags == 8192`).
- **GPU Acceleration:** Built with PyTorch CUDA support (`cuda:0`) and half-precision (`fp16`) for fast audio transcription.
- **Async Execution:** Runs ML inference in background threads (`asyncio.to_thread`) to ensure the bot stays responsive.

---

## Quick Setup

### 1. Requirements

- Windows 10/11 with an NVIDIA GPU
- Anaconda / Miniconda
- Python 3.11

### 2. Environment Setup

```powershell
# Create & activate a Python 3.11 environment
conda create -n sttbot python=3.11 -y
conda activate sttbot

# Install PyTorch with CUDA 12.1 support
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)

# Install required dependencies
pip install discord.py soundfile transformers python-dotenv
