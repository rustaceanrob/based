import discord
from dotenv import load_dotenv
import os
import requests
from metaphor_python import Metaphor
from openai import OpenAI

load_dotenv()
APEX = os.environ["APEX_TOKEN"]

endpoints = { "mempool": "https://www.blockstream.info/api/mempool/recent", "height":  "https://www.blockstream.info/api/blocks/tip/height",
              "mempool_stats":  "https://www.blockstream.info/api/mempool", "fees": "https://www.blockstream.info/api/fee-estimates",
              "price": "https://api.coinbase.com/v2/exchange-rates?currency=BTC", "tip": "https://blockstream.info/api/blocks/tip/hash",
              "apex": "https://api.mozambiquehe.re/maprotation?auth=" + APEX + "&version=2"}

## get the apex map rotation
def get_apex():
    response = requests.get(endpoints["apex"])

    if response.status_code == 200:
        data = response.json()
        pubs_now = data["battle_royale"]["current"]["map"]
        pubs_next = data["battle_royale"]["next"]["map"]
        rotation = data["battle_royale"]["current"]["remainingMins"]
        ranked = data["ranked"]["current"]["map"]
        digest = "the current pubs map is " + str(pubs_now) + " for " + str(rotation) + " remaining minutes\n"
        digest = digest + "the next pubs map is " + str(pubs_next) + " and the current ranked map is " + str(ranked) +"\n"
        return digest
    else:
        print(f"Error: {response.status_code}")

## get the 10 most recent transactions in the mempool
def get_mempool():
    response = requests.get(endpoints["mempool"])

    if response.status_code == 200:
        data = response.json()
        formatted_string = ""
        for tx in data:
            formatted_string = formatted_string + "`" + str(tx) + "`" + "\n\n"

        return "recent bitcoin transactions: \n\n" + formatted_string
    else:
        print(f"Error: {response.status_code}")

## current height of the bitcoin blockchain
def get_height():
    response = requests.get(endpoints["height"])

    if response.status_code == 200:
        data = response.json()
        return str(data)
    else:
        print(f"Error: {response.status_code}")

## get global mempool stats
def get_mempool_stats():
    response = requests.get(endpoints["mempool_stats"])

    if response.status_code == 200:
        data = response.json()
        return (data["count"], data["vsize"], data["total_fee"])
    else:
        print(f"Error: {response.status_code}")

## bitcoin fees in vb
def get_fees():
    response = requests.get(endpoints["fees"])

    if response.status_code == 200:
        data = response.json()
        return (round(data["1"],2), round(data["5"],2), round(data["10"],2))
    else:
        print(f"Error: {response.status_code}")

## fiat price
def get_price():
    response = requests.get(endpoints["price"])
    try:
        if response.status_code == 200:
            data = response.json()
            return "price: $" + data["data"]["rates"]["USD"]
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(e)
        return "0"

## current blockchain chaintip
def get_chaintip():
    response = requests.get(endpoints["tip"])
    if response.status_code == 200:
        data = response.json()
        print(data)
        return str(data)
    else:
        print(f"Error: {response.status_code}")

## gets a response from gpt
def get_code(prompt):
    TOKEN = os.environ["OPEN_AI_TOKEN"]
    client = OpenAI(api_key=TOKEN)
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": prompt},]
    )
    return response.choices[0].message.content

## searches for relevant articles and returns a list of 5
def metaphor_search(prompt):
    TOKEN = os.environ["METAPHOR_TOKEN"]
    metaphor = Metaphor(TOKEN)
    response = metaphor.search(
        prompt,
        num_results=5,
        use_autoprompt=True,
    )

    formatted_string = ""
    for res in response.results:
        formatted_string = formatted_string + f"[{res.title}]({res.url})" + "\n\n"

    return "relevant links: \n\n" + formatted_string

## message handler
def handle_message(content):
    message = content.lower()

    if message == "$mempool":
        mempool = get_mempool()
        return mempool
    
    if message == "$bitcoin":
        response = ""

        height = get_height()
        response = "current block height: " + height + "\n\n"
        (count, size, fee) = get_mempool_stats()
        response = response + f"transactions in the mempool: {count}, \nmempool size: {size} vBytes, \ntotal fee {round(fee / 10_000_000, 2)} bitcoin\n\n"
        (next, five, ten) = get_fees()
        response = response + f"fees for next block confirmation: {next} sat/vb, five blocks: {five} sat/vb, 10 blocks: {ten} sat/vb \n\n"
        price = get_price()
        response = response + price

        return response
    
    if "$search" in message:
        prompt = message.split("$search")[1]
        response = metaphor_search(prompt=prompt)
        return response

    if "$code" in message:
        prompt = message.split("$code")[1]
        response = get_code(prompt=prompt)
        return response

    if message == "$apex":
        maps = get_apex()
        return maps
    
    return 

## send a message back to the channel that requested it
async def send_message(message, content):
    try:
        response = handle_message(content=content)
        await message.channel.send(response)
    except Exception as e:
        print(e)

## run the bot and ignore events that the bot sent itself
def run_bot():
    TOKEN = os.environ['DISCORD_TOKEN']
    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f'{client.user} is running')

    @client.event
    async def on_message(message):
        content = message.content

        if message.author == client.user:
            return
        
        # log:
        # username = str(message.author)
        # user_message = str(message.content)
        # channel = str(message.channel)

        await send_message(message=message, content=content)
            
    client.run(TOKEN)

if __name__ == "__main__":
    run_bot()