# YapHelper 

A Discord bot that transcribes native Discord voice messages into text using Groq's fast Whisper API.

---

## Features

- **Voice Message Support:** Listens to native Discord voice notes (`message.flags == 8192`).
- **Groq API Cloud Inference:** Transcribes audio using `whisper-large-v3` without requiring local GPU/RAM.
- **24/7 Hosting:** Built to deploy lightweight on free cloud platforms like Render.

---

## Setup & Running

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/Rizlem/yaphelper.git](https://github.com/Rizlem/yaphelper.git)
   cd yaphelper
