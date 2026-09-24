import os
import asyncio
import discord
import soundfile as sf
import torch
from discord.ext import commands
from dotenv import load_dotenv
from transformers import pipeline
from time import perf_counter

# loads .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# sets up either gpu/cpu interface
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# loads whisper model when bot starts up
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    chunk_length_s=30,
    device=device,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# utilises pipeline to transcribe, and returns with text
def transcribe(audio_dict):
    return pipe(audio_dict, batch_size=8)["text"]

# checks if the flag is = 8192 - the flag value for a voice note
def isvoicenote(messagedata):
    return messagedata.flags.value == 8192

# initialise bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")


# transcription command code
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
        
        # read audio and sampling rate
        data, sample_rate = sf.read("voicenote.ogg")
        
        # convert stereo to mono audio
        if data.ndim > 1:
            data = data.mean(axis=1)
        
        audio_dict = {
            "raw": data,
            "sampling_rate": sample_rate
        }
        
        # run interface in thread pool so bot stays active

        # test the time taken (to 3dp) to perform action
        start = perf_counter()
        await ctx.send (await asyncio.to_thread(transcribe, audio_dict))
        end = perf_counter()
        await ctx.send(f"took {round((end-start),3)} seconds to transcribe")
        if os.path.exists("voicenote.ogg"):
            os.remove("voicenote.ogg")
    else: 

        # if doesnt pass all voice note check tests, default response
        await ctx.send("This is not a voice note.")

bot.run(TOKEN)

