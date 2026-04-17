import asyncio
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

langleyTownshipLink = "https://tol.njoyn.com/CL3/xweb/Xweb.asp?tbtoken=bFhRRxMXCG91FHV5RFJTCCNKcRFEcCVbe0hZJysPE2NcWzJpWzEfchd9BQkbURNUTncqWA%3D%3D&chk=ZVpaShw%3D&CLID=56677&page=joblisting"
abbotsfordCityLink = "https://abbotsford.njoyn.com/CL3/xweb/Xweb.asp?tbtoken=bVtaRRwXCBhxFAEDR11RCFFKdmVEcFFcdkggVCwOExBZW0AZX0sac2R8cwkbURBQS3cqWA%3D%3D&chk=ZVpaShw%3D&CLID=55227&page=joblisting"

criteria = ["IT", "Technical Support", "Information Technology", "Systems Analyst"]

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.binary_location = "/usr/bin/chromium-browser"
options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
service = Service("/usr/bin/chromedriver")


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
        scanLangleyTownship()
        scanCityOfAbbotsford()
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
def scanLangleyCity():
    print("\nScanning Langley City \n")
    response = requests.get("https://www.langleycity.ca/careers")
    html = response.text
    
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any(term in cell for cell in cells for term in criteria):
            postings.append(cells)
    for row in soup.select(".view-job-postings .views-row"):
        title = row.select_one(".views-field-title").get_text(strip=True)
        if "IT" in title:
            closing = row.select_one(".views-field-field-date").get_text(strip=True)
            comp_num = row.select_one(".views-field-field-competition-number").get_text(strip=True)
            emp_type = row.select_one(".views-field-field-employment-type").get_text(strip=True)
            post = ([title, closing, comp_num, emp_type])
            postings.append(post)


def scanChilliwackCity():
    print("\nScanning Chilliwack City \n")
    response = requests.get("https://jobs.chilliwack.com/postings/")
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any(term in cell for cell in cells for term in criteria):
            postings.append(cells)
            print(cells)

def scanLangleyTownship():
    print("\nScanning Langley Township \n")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(langleyTownshipLink)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "NjnSectionTable"))
    )

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any(term in cell for cell in cells for term in criteria):
            postings.append(cells)
            print(cells)


def scanCityOfAbbotsford():
    print("\nScanning City of Abbotsford\n")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(abbotsfordCityLink)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "NjnSectionTable"))
    )

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.find_all("tr"):
        cells = [td.get_text() for td in row.find_all("td")]
        if any(term in cell for cell in cells for term in criteria):
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
        postings.append("=== Township of Langley ===")
        scanLangleyTownship()
        postings.append("=== City of Abbotsford ===")
        scanCityOfAbbotsford()


        diff = "\n".join(context_diff([str(p) for p in postingPrevious], [str(p) for p in postings]))
        print(diff)
        if postings:
            Sentmessage = "\n".join(map(str, postings))
        else:
            Sentmessage = "No postings found"
        postings.remove("=== Chilliwack City ===")
        postings.remove("=== Langley City ===")
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)
    if message.content.lower().startswith('!test'):
        print("Test Started")
        Sentmessage = 'Test Complete'.format(message)
        print('No functions currently being tested')
        print(Sentmessage)

client.run(TOKEN)
