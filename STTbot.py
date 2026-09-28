import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def isvoicenote(messagedata):
    return messagedata.flags.value == 8192

# Synchronous Groq API calls (run via asyncio.to_thread)
def groq_transcribe(file_path):
    with open(file_path, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    return transcription

def groq_summarise(text):
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",  
        messages=[
            {
                "role": "system",
                "content": "You summarize informal spoken voice note transcriptions into concise, 1-2 sentence summaries or clean bullet points." 
            },
            {
                "role": "user",
                "content": f"Summarize this voice note transcript:\n\n{text}"
            }
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content

@bot.command()
async def scribe(ctx):
    if ctx.message.reference is None:
        await ctx.send("Please reply to a voice note.")
        return

    message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    if isvoicenote(message):
        voicenote = message.attachments[0]
        await voicenote.save("voicenote.ogg")
        
        # Offload transcription to Groq LPU
        transcription = await asyncio.to_thread(groq_transcribe, "voicenote.ogg")
        await ctx.send(transcription)
        
        if os.path.exists("voicenote.ogg"):
            os.remove("voicenote.ogg")
    else:
        await ctx.send("This is not a voice note.")

@bot.command()
async def sum(ctx):
    if ctx.message.reference is None:
        await ctx.send("Please reply to a voice note.")
        return

    message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    if isvoicenote(message):
        voicenote = message.attachments[0]
        await voicenote.save("voicenote.ogg")
        
        # Transcribe & Summarize via Groq
        transcription = await asyncio.to_thread(groq_transcribe, "voicenote.ogg")
        summary = await asyncio.to_thread(groq_summarise, transcription)
        
        await ctx.send(summary)

        if os.path.exists("voicenote.ogg"):
            os.remove("voicenote.ogg")
    else:
        await ctx.send("This is not a voice note.")

bot.run(TOKEN)