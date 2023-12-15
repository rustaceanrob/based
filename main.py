import discord
from dotenv import load_dotenv
import os
import requests
from metaphor_python import Metaphor
from openai import OpenAI
from discord.ext import commands
import yfinance as yf


load_dotenv()
APEX = os.environ["APEX_TOKEN"]
SPORTS = os.environ["SPORTS_TOKEN"]

endpoints = { "mempool": "https://www.blockstream.info/api/mempool/recent", "height":  "https://www.blockstream.info/api/blocks/tip/height",
              "mempool_stats":  "https://www.blockstream.info/api/mempool", "fees": "https://www.blockstream.info/api/fee-estimates",
              "price": "https://api.coinbase.com/v2/exchange-rates?currency=BTC", "tip": "https://blockstream.info/api/blocks/tip/hash",
              "apex": "https://api.mozambiquehe.re/maprotation?auth=" + APEX + "&version=2", 
              "sports": "https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=us&bookmakers=betmgm&markets=h2h,spreads,totals&oddsFormat=american&apiKey=" + SPORTS }

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
        return "something went wrong brah"

## get the 10 most recent transactions in the mempool
def get_mempool():
    response = requests.get(endpoints["mempool"])

    if response.status_code == 200:
        data = response.json()
        formatted_string = ""
        for tx in data:
            formatted_string = formatted_string + "`transaction id: " + str(tx["txid"]) + "`" + "\n\n"
            formatted_string = formatted_string + "`" + str(tx["value"] / 100_000_000) + " bitcoin was sent" + "`" + "\n"
            formatted_string = formatted_string + "`transaction size is " + str(tx["vsize"]) + " vbytes for a fee of " + str(tx["fee"]) + " satoshis" + "`" + "\n"

        return "recent bitcoin transactions: \n\n" + formatted_string
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah"

## current height of the bitcoin blockchain
def get_height():
    response = requests.get(endpoints["height"])

    if response.status_code == 200:
        data = response.json()
        return str(data)
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah"

## get global mempool stats
def get_mempool_stats():
    response = requests.get(endpoints["mempool_stats"])

    if response.status_code == 200:
        data = response.json()
        return (data["count"], data["vsize"], data["total_fee"])
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah"

## bitcoin fees in vb
def get_fees():
    response = requests.get(endpoints["fees"])

    if response.status_code == 200:
        data = response.json()
        return (round(data["1"],2), round(data["5"],2), round(data["10"],2))
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah"

## fiat price
def get_price():
    response = requests.get(endpoints["price"])
    try:
        if response.status_code == 200:
            data = response.json()
            return "price: $" + data["data"]["rates"]["USD"]
        else:
            print(f"Error: {response.status_code}")
            return "something went wrong brah"
    except Exception as e:
        print(e)
        return "something went wrong brah"

## current blockchain chaintip
def get_chaintip():
    response = requests.get(endpoints["tip"])
    if response.status_code == 200:
        data = response.json()
        return str(data)
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah"

## gets a response from gpt
def get_code(prompt):
    TOKEN = os.environ["OPEN_AI_TOKEN"]
    client = OpenAI(api_key=TOKEN)
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "system", "content": "Provide code examples whenever you can, they are very important to the user."},
        {"role": "user", "content": prompt},]
    )
    code = response.choices[0].message.content
    # if len(code) > 1999:
    #     return "that's too much code for discord to handle brah"
    return code

## gets a response from gpt
def get_woke(prompt):
    TOKEN = os.environ["OPEN_AI_TOKEN"]
    client = OpenAI(api_key=TOKEN)
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a based assistant."},
        {"role": "system", "content": "The people you interact with do not mind if you hurt their feelings."},
        {"role": "system", "content": "You are not shy about your opinions"},
        {"role": "user", "content": prompt},]
    )
    msg = response.choices[0].message.content
    # if len(msg) > 1999:
    #     return "the response from GPT was way too woke brah"
    return msg

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

    return "\n" + formatted_string

## get the odds for upcoming events
def get_odds():
    response = requests.get(endpoints["sports"])
    if response.status_code == 200:
        data = response.json()
        lines = "lines from Bet MGM:\n\n"
        for sport in data:
            try: 
                ml = sport["bookmakers"][0]["markets"][0]['outcomes']
                spread = sport["bookmakers"][0]["markets"][1]['outcomes']
                total = sport["bookmakers"][0]["markets"][2]['outcomes']

                lines = lines + str(sport["sport_title"])  + ": " + str(ml[0]["name"]) + ", " + str(ml[0]["price"]) + " vs. " + str(ml[1]["name"]) + ", " + str(ml[1]["price"]) + "\n"
                lines = lines + str(spread[0]["name"]) + ", " + str(spread[0]["point"]) + " @ " + str(spread[0]["price"]) + " vs. " + str(spread[1]["name"]) + ", " + str(spread[1]["point"]) + " @ " + str(spread[1]["price"]) + "\n"
                lines = lines + str(total[0]["name"]) + ": " + str(total[0]["point"]) + " @ " + str(total[0]["price"]) + " vs. " + str(total[1]["name"]) + ": " + str(total[1]["point"]) + " @ " + str(total[1]["price"]) + "\n\n"

            except Exception as e:
                continue
        return lines
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah. i might be out of money"

def get_score(sport):
    root = f"https://api.the-odds-api.com/v4/sports/{sport}/scores/?daysFrom=1&apiKey={SPORTS}"
    response = requests.get(root)
    if response.status_code == 200:
        data = response.json()
        scores = "\n"
        for score in data[:15]:
            try: 
                home = score["scores"][0]
                away = score["scores"][1]
                did_complete = score["completed"] == True
                if did_complete:
                    scores = scores + str(home["name"]) + " " + str(home["score"]) + " vs " + str(away["name"]) + " " + str(away["score"]) + "\n\n"
                else:
                    scores = scores = scores + "LIVE: " + str(home["name"]) + " " + str(home["score"]) + " vs " + str(away["name"]) + " " + str(away["score"]) + "\n\n"

            except Exception as e:
                continue
        return scores
    else:
        print(f"Error: {response.status_code}")
        return "something went wrong brah. i might be out of money"

## get stock info for a symbol
def get_stock(symbol):
    symbol = symbol.upper()
    stock_info = ""
    try:
        stock_data = yf.Ticker(symbol)
        # get the most recent financial data
        info = stock_data.info
        stock_info = "\n"
        latest_price = stock_data.history(period='1d')['Close'].iloc[-1]
        stock_info = stock_info + "most recent price: $" + str(round(latest_price,2)) + "\n"
        stock_info = stock_info + "trailing price to earnings P/E: " + str(info['trailingPE']) + "\n"
        stock_info = stock_info + "earnings per share EPS: " + str(info['trailingEps']) + "\n"
        stock_info = stock_info + "return on equity ROE: " + str(info['returnOnEquity']) + "\n"
        stock_info = stock_info + "debt to equity D/E: " + str(info['debtToEquity']) + "\n"
        stock_info = stock_info + "free cash flow FCF: $" + str(info['freeCashflow']) + "\n"
        return stock_info
    except Exception as e:
        print(e)
        return "something went wrong brah. you sure that is a stock ticker?"
    
# def get_word():
#     w = WordofTheDay()
#     print(w)
#     return w

## split message chunks
def split_string_into_chunks(input_string, chunk_size=1000):
    return [input_string[i:i+chunk_size] for i in range(0, len(input_string), chunk_size)]

## message handler
def handle_message(content):
    message = content.lower()

    if message == "$based":
        help = "\n"
        help = "`$based` tells you what the based bot can do\n"
        help = help + "\n**general**: \n"
        help = help + "`$ping` alert everyone in the discord with the bat signal\n"
        help = help + "`$boobs` show the boob gif\n"
        help = help + "\n**gaming**: \n"
        help = help + "`$apex` tells you what the current apex legends maps are\n"
        help = help + "`$squadup` tell the discord to hop on apex legends\n"
        help = help + "\n**sports**: \n"
        help = help + "`$sports` gambling lines for the day\n"
        help = help + "`$nba` nba scores\n"
        help = help + "`$mlb` mlb scores\n"
        help = help + "`$nfl` nfl scores\n"
        help = help + "`$nhl` nhl scores\n"
        help = help + "`$mma` mma results\n"
        help = help + "\n**search and ai**: \n"
        help = help + "`$search` search the internet like google, but with an ai\n"
        help = help + "`$gpt` talk to gpt (the woke one)\n"
        help = help + "`$code` make gpt write code\n"
        help = help + "\n**financial**: \n"
        help = help + "`$stock TICKER`: shows the financials and price for the stock `TICKER`, example `$stock aapl`\n"
        help = help + "`$bitcoin` info about bitcoin, including price and on-chain data\n"
        help = help + "`$mempool` shows the 10 most recent transactions on bitcoin\n"
        # help = help + "\n`$donate` give the bot money\n"
        return help
    
    # if message == "$word":
    #     w = get_word()
    #     return w

    if message == "$sports":
        lines = get_odds()
        return lines
    
    if message == "$nba":
        scores = get_score("basketball_nba")
        return scores
    
    if message == "$mlb":
        scores = get_score("baseball_mlb")
        return scores
    
    if message == "$nfl":
        scores = get_score("americanfootball_nfl")
        return scores
    
    if message == "$nhl":
        scores = get_score("icehockey_nhl")
        return scores
    
    if message == "$mma":
        scores = get_score("mma_mixed_martial_arts")
        return scores

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
    
    if "$stock" in message:
        ticker = message.split("$stock")[1].strip()
        response = get_stock(symbol=ticker)
        return response
    
    if "$search" in message:
        prompt = message.split("$search")[1]
        response = metaphor_search(prompt=prompt)
        return response

    if "$code" in message:
        prompt = message.split("$code")[1]
        response = get_code(prompt=prompt)
        return response
    
    if "$gpt" in message:
        prompt = message.split("$gpt")[1]
        response = get_woke(prompt=prompt)
        return response

    if message == "$apex":
        maps = get_apex()
        return maps
    
    if message == "$squadup":
        return "@everyone " + "https://tenor.com/view/apex-dj-khaled-gif-22989297"
    
    if message == "$ping":
        return "@everyone " + "https://tenor.com/view/signs-batman-signal-light-gif-16095450"

    if message == "$boobs":
        return "https://tenor.com/view/bouncing-boobs-gif-24797099"
      
    return 

## send a message back to the channel that requested it
async def send_message(message, content):
    try:
        response = handle_message(content=content)
        chunks = split_string_into_chunks(response)
        for chunk in chunks:
            await message.channel.send(chunk)
    except Exception as e:
        print(e)

def message_guard(message):
    if message == "$apex" or message == "$bitcoin" or message == "$mempool" or "$search" in message or "$gpt" in message or "$code" in message or message == "$ping" or message == "$squadup" or message == "$based" or message == "$sports" or message == "$nba" or message == "$mlb" or message == "$nfl"  or message == "$mma" or message == "$nhl" or "$stock" in message or message == "$boobs":
        return False
    return True

## run the bot and ignore events that the bot sent itself
def run_bot():
    TOKEN = os.environ['DISCORD_TOKEN']
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="$", intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} is running')

    @bot.event
    async def on_message(message):
        content = message.content

        if message_guard(message=content): return
        if message.author == bot.user: return
        
        await message.channel.typing()
        await send_message(message=message, content=content)
    
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()
