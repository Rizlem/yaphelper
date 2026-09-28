# Discord Voice Note Transcriber & Summarizer

A fast, lightweight Discord bot that transcribes and summarizes voice notes on demand. Instead of relying on expensive local hardware and heavy machine learning models, this bot offloads inference to the **Groq Cloud API**, providing near-instant responses using Language Processing Units (LPUs).

## Features
* **Instant Transcriptions:** Reply to any voice note with `!scribe` to get a highly accurate text transcription powered by Whisper Large V3.
* **Smart Summaries:** Reply with `!sum` to get a concise, conversational summary of the voice note powered by open-source LLMs (GPT-OSS-20B) via Groq.
* **Lightweight & Cloud-Ready:** No local GPUs, CUDA drivers, or massive VRAM requirements needed. Can be hosted easily on a cheap CPU VPS or Raspberry Pi.

## Prerequisites
Before running the bot, you will need:
* **Python 3.8+** installed.
* A **Discord Bot Token** from the [Discord Developer Portal](https://discord.com/developers/applications). Ensure the **Message Content Intent** is enabled.
* A **Groq API Key** from the [Groq Cloud Console](https://console.groq.com/).

##  Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/discordstt.git](https://github.com/your-username/discordstt.git)
   cd discordstt