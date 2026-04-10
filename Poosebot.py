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
from difflib import context_diff

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def setup_hook(self):
        pass


async def runLoop(channel):
    while True:
        print("Working")
        postingPrevious = postings.copy()
        postings.clear()
        scanLangleyCity()
        scanChilliwackCity()
        diff = "\n".join(context_diff([str(p) for p in postingPrevious], [str(p) for p in postings]))
        print("Postings:")
        print("\n".join(map(str, postings)))
        print("Prev")
        print("\n".join(map(str, postingPrevious)))
        print (diff)
        if (diff != ""):
            Sentmessage = diff
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await channel.send(embed=embed)
        await asyncio.sleep(3600)  
client = MyClient(intents=intents)

postings = []
postingPrevious = []

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    print(f'Using Channel {channel}')
    if channel:
        client.loop.create_task(runLoop(channel))
    else:
        print("Channel not found. Please check the CHANNEL_ID.")
''' Old function Not currently needed
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
'''
def scanLangleyCity():
    response = requests.get("https://www.langleycity.ca/careers")
    html = response.text
    
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any("IT" in cell for cell in cells):
            postings.append(cells)
            #print(postings)
    for row in soup.select(".view-job-postings .views-row"):
        title = row.select_one(".views-field-title").get_text(strip=True)
        if "IT" in title:
            closing = row.select_one(".views-field-field-date").get_text(strip=True)
            comp_num = row.select_one(".views-field-field-competition-number").get_text(strip=True)
            emp_type = row.select_one(".views-field-field-employment-type").get_text(strip=True)
            post = ([title, closing, comp_num, emp_type])
            postings.append(post)


def scanChilliwackCity():
    response = requests.get("https://jobs.chilliwack.com/postings/")
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any("IT" in cell for cell in cells):
            postings.append(cells)
            print(cells)


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
    if message.content.lower().startswith('!scan'):
        postingPrevious = postings.copy()
        postings.clear()
        postings.append("=== Langley City ===")
        scanLangleyCity()
        postings.append("=== Chilliwack City ===")
        scanChilliwackCity()

        diff = "\n".join(context_diff([str(p) for p in postingPrevious], [str(p) for p in postings]))
        print(diff)
        if postings:
            Sentmessage = "\n".join(map(str, postings))
        else:
            Sentmessage = "No postings found"
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)
    if message.content.lower().startswith('!test'):
        Sentmessage = 'Test Complete'.format(message)
        scanChilliwackCity()
        print(Sentmessage)

client.run(TOKEN)
