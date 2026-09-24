import os
import discord
from playsound import playsound
from discord.ext import commands
from dotenv import load_dotenv
import IPython.display as ipd
import soundfile as sf
import torch
from huggingface_hub import login
from diffusers import AutoPipelineForText2Image
from transformers import pipeline

#specifies what device to use for processing the model
device = "cuda:0" if torch.cuda.is_available() else "cpu"

#uses the model to transcribe the audio fetched from the discord chat
def transcribe(audio_dict):
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        chunk_length_s=30,
        device=device,
    )
    # the hugging face pipeline expects keys: "raw" and "sampling_rate"
    return pipe(audio_dict, batch_size=8)["text"]
    
#checks if a certain message is a voice note
#discord flags each voice note message with the code 8192
def isvoicenote(messagedata):
    if messagedata.flags.value == 8192:
        return True
    else: return False

#loads environment variables from the .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

#defines required intents
intents = discord.Intents.default()
intents.message_content = True

#initialises bot
bot = commands.Bot(command_prefix="!", intents=intents)

#event triggers when bot logs on
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

#the scribe command line
@bot.command()
async def scribe(ctx):
    #checks if there is any reply to begin with
    if ctx.message.reference is None:
        return

    #stores the message id of the replied message
    messageid = ctx.message.reference.message_id

    #stores the message of the replied message
    message = await ctx.channel.fetch_message(messageid)

    #checks if replied message is a voice note
    if isvoicenote(message):
        voicenote = message.attachments[0]
        await voicenote.save("voicenote.ogg")
        
        #reads the saved audio file
        data, sample_rate = sf.read("voicenote.ogg")
        
        #converts from stereo to mono if needed
        if data.ndim > 1:
            data = data.mean(axis=1)
        
        #formats the dictionary so it is suitable for the huggingface pipeline
        audio_dict = {
            "raw": data,
            "sampling_rate": sample_rate
        }
        
        #calls the pipeline, and returns the transcription via the bot
        text = transcribe(audio_dict)
        await ctx.send(text) 
    else: 
        #sends this message if replied message is not a voice note
        await ctx.send(f"this is not a voice note")
    
# Run the bot using the loaded variable
bot.run(TOKEN)