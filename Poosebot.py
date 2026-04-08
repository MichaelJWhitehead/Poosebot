import asyncio
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import difflib

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 
CISchanges = ""
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def setup_hook(self):
        pass


async def runLoop(channel):
    while True:
        global CISchanges
        getTimeTableChanges()
        with open('timetable_changes.txt', 'r') as file:
            lines = file.readlines()
        if CISchanges != "":   
            Sentmessage = CISchanges
            CISchanges = ""
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await channel.send(embed=embed)
        else:
            print("No CIS changes found.")
        await asyncio.sleep(3600)  
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        client.loop.create_task(runLoop(channel))
    else:
        print("Channel not found. Please check the CHANNEL_ID.")

def getScreenshotOfClass(url, id, outputfile):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, id))
        )
        element.screenshot(outputfile)
        print("Screenshot Taken")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
    finally:
        driver.quit()

Sentmessage = ""
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith('!ping'):
        Sentmessage = 'pong'.format(message)
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

client.run(TOKEN)
