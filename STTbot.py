import os
import asyncio
import discord
import soundfile as sf
import torch
from discord.ext import commands
from dotenv import load_dotenv
from transformers import pipeline
from time import perf_counter

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup GPU/CPU device
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load Whisper model ONCE on bot startup
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    chunk_length_s=30,
    device=device,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

def transcribe(audio_dict):
    return pipe(audio_dict, batch_size=8)["text"]

def isvoicenote(messagedata):
    return messagedata.flags.value == 8192

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

@bot.command()
async def scribe(ctx):
    if ctx.message.reference is None:
        await ctx.send("Please reply to a voice note.")
        return

    messageid = ctx.message.reference.message_id
    message = await ctx.channel.fetch_message(messageid)

    if isvoicenote(message):
        voicenote = message.attachments[0]
        await voicenote.save("voicenote.ogg")
        
        # Read audio array & sampling rate
        data, sample_rate = sf.read("voicenote.ogg")
        
        # Downmix stereo to mono if needed
        if data.ndim > 1:
            data = data.mean(axis=1)
        
        audio_dict = {
            "raw": data,
            "sampling_rate": sample_rate
        }
        
        # Run inference in a thread pool so bot stays active
        start = perf_counter()
        await ctx.send (await asyncio.to_thread(transcribe, audio_dict))
        end = perf_counter()
        await ctx.send(f"took {round((end-start),3)} seconds to transcribe")
    else: 
        await ctx.send("This is not a voice note.")

bot.run(TOKEN)

