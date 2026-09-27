import os
import asyncio
import discord
import soundfile as sf
import torch
from discord.ext import commands
from dotenv import load_dotenv
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from huggingface_hub import login

# loads .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# sets up either gpu/cpu interface
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# loads summariser pipeline
sumname = "philschmid/bart-large-cnn-samsum"
tokenizer = AutoTokenizer.from_pretrained(sumname)
model = AutoModelForSeq2SeqLM.from_pretrained(sumname, use_safetensors=True).to(device)

# loads speech recognition pipeline
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

#converts .ogg file into a dictionary with raw and sampling rate data
async def convert(message):
    voicenote = message.attachments[0]
    await voicenote.save("voicenote.ogg")
            
    # read audio and sampling rate
    data, sample_rate = sf.read("voicenote.ogg")
            
    # convert stereo to mono audio
    if data.ndim > 1:
        data = data.mean(axis=1)
            
    return ({
        "raw": data,
        "sampling_rate": sample_rate
     })

# checks if the flag is = 8192 - the flag value for a voice note
def isvoicenote(messagedata):
    return messagedata.flags.value == 8192

# summarises message by tokenizing, then generating an output usingg the tokens, then decoding the output (which will be stored as tokens)
def summarise(message):
    inputs = tokenizer.encode(message, return_tensors="pt", max_length=512, truncation=True).to(device)
    summary_ids = model.generate(inputs, max_length=60, min_length=10, length_penalty=1.2, num_beams=4, no_repeat_ngram_size=3, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# initialise bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# shows the bot is up and running
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")


# transcription command code
@bot.command()
async def scribe(ctx):
    # checks if there is a replied message
    if ctx.message.reference is None:
        await ctx.send("Please reply to a voice note.")
        return

    # stores message id, then uses message id to fetch message data
    messageid = ctx.message.reference.message_id
    message = await ctx.channel.fetch_message(messageid)

    if isvoicenote(message):
        audio_dict = await convert(message)
        
        # run interface in thread pool so bot stays activ
        sumcache = await asyncio.to_thread(transcribe, audio_dict)
        await ctx.send(sumcache)

        #function automatically creates a voice note, so code will remove it once it is formed
        if os.path.exists("voicenote.ogg"):
            os.remove("voicenote.ogg")
    else: 

        # if doesnt pass all voice note check tests, default response
        await ctx.send("This is not a voice note.")


@bot.command()
async def sum(ctx):
    # checks if a replied voice note exists
    if ctx.message.reference is None:
        await ctx.send("Please reply to a voice note.")
        return
    
    # stores message id, then uses message id to fetch message data
    messageid = ctx.message.reference.message_id
    messageinfo = await ctx.channel.fetch_message(messageid)


    #checks if message is a voice note, if so, converts the message, transcribes it and runs the transcription through summarise()
    if isvoicenote(messageinfo):
        audio_dict = await convert(messageinfo)
        text = await asyncio.to_thread(transcribe, audio_dict)
        summary = await asyncio.to_thread(summarise, text)
        await ctx.send(summary)

        if os.path.exists("voicenote.ogg"):
            os.remove("voicenote.ogg")
    else:
        await ctx.send("This is not a voice note.")


bot.run(TOKEN)