import discord
import random
import datetime
import requests
import os
import psycopg2
from urllib import parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Connecting to postgres DATABASE
parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()

counter = 0
client = discord.Client()
congrats = ['Congrats', 'congrats', 'Congratulations', 'congratulations', 'Congratulation', 'congratulation']
channelToId = {'general': '409164584008548354', 'botIdea': '414063833217237002', 'botControl': '409193276885958659', 'tts': '414011036505604096'}
jokes = []
pickupLines = []
googleToken = os.environ.get('googleToken')


helpMenu = """-----HELP-----
!SPR        - Scissors Paper Rock -- Usage: !SPR choice
!guess      - Guess a number between 1 and 10 
!flip       - Flip a coin
!ping       - Pong
!joke       - These are offensive you have been warned
!flirt      - Flirt with a bot - you lonely bastard 
!coords     - Get coordinates of an address
!insult     - Insult someone
!request    - Request a feature -- Usage: !request "Feature"
!urban      - Queries Urban dictionary -- Usage: !urban "word"
-----END-----
"""




@client.event
async def on_ready():
    # await client.edit_profile(username=os.environ.get('BotUsername'))
    await client.change_presence(game=discord.Game(name=os.environ.get('game')))
    logger('Logged in as')
    logger(client.user.name)
    logger(client.user.id)
    logger("--------")


@client.event
async def on_member_join(member):
    await client.send_message(client.get_channel(channelToId['general']), "Welcome bitch!")
    logger(member)
    

@client.event
async def on_message(message):
    global counter
    counter += 1
    if message.content.startswith("!request"):
        received = saveIdeas(message)
        if received:
            await client.send_message(message.channel, "Feature Request Received!")
        else:
            await client.send_message(message.channel, "Fuck Something went wrong!")

    now = datetime.datetime.now()
    logger("{} -- {} : {}".format(message.author, message.channel, message.content))
    if message.author == client.user:
        return

    if counter == 10:
        await client.send_message(message.channel, '#litfam')
        counter = 0

    # in chat stuff
    for item in congrats:
        if item in message.content:
            await client.send_message(message.channel, ':tada:')
            return

    if 'gucci' in message.content.lower():
        await client.send_message(message.channel, 'Kill Your Self :rage:')

    if 'haha' in message.content.lower():
        await client.send_message(message.channel, ':joy:')

    if 'bot' in message.content.lower():
        typeOfMessage = random.randint(0, 1)
        if typeOfMessage:
            await client.send_message(message.channel, 'Someone say bot!')
            resp = await client.wait_for_message(timeout=5)
            if resp is not None:
                if 'no' in resp.content.lower():
                    await client.send_message(message.channel, "Fk You!")
        else:
            await client.send_message(message.channel, "What!")

    # Functions/ commands

    if message.content.startswith("!help"):
        await client.send_message(message.channel, helpMenu)

    if message.content.startswith("!flip"):
        choice = random.randint(0, 1)
        if choice:
            output = "Heads!"
        else:
            output = "Tails!"
        await client.send_message(message.channel, output)

    if message.content.startswith('!ping'):
        await client.send_message(message.channel, 'pong')

    if message.content.startswith('!kick'):
        member = message.content.split(' ')[1]
        client.kick(member)

    if message.content.startswith("!joke"):
        if len(jokes) == 0:
            getJokes()

        jokeIndex = random.randint(0, len(jokes)-1)
        joke = jokes[jokeIndex]
        await client.send_message(message.channel, joke)
        del jokes[jokeIndex]

    if message.content.startswith("!flirt"):
        if len(pickupLines) == 0:
            pickupParse()

        pickupIndex = random.randint(0, len(pickupLines)-1)
        line = pickupLines[pickupIndex]
        await client.send_message(message.channel, line)
        del pickupLines[pickupIndex]

    if message.content.startswith('!guess'):
        await client.send_message(message.channel, 'Guess a number between 1 to 10')

        def guess_check(m):
            return m.content.isdigit()

        guess = await client.wait_for_message(timeout=5.0, author=message.author, check=guess_check)
        answer = random.randint(1, 10)
        if guess is None:
            fmt = 'Sorry, you took too long. It was {}.'
            await client.send_message(message.channel, fmt.format(answer))
            return
        if int(guess.content) == answer:
            await client.send_message(message.channel, 'You are right!')
        else:
            await client.send_message(message.channel, 'Sorry. It is actually {}.'.format(answer))

    if message.content.startswith("!SPR") or message.content.startswith("!spr"):
        userChoice = message.content.split(" ")[1]
        result = game(userChoice)
        msg = "I chose {} you choose {}\n{}".format(result[1], userChoice, result[0])
        await client.send_message(message.channel, msg)

    if message.content.startswith("!coords"):
        address = message.content.replace("!coords", '')
        coords = getCoords(address)
        await client.send_message(message.channel, "{}\nLat:{} - Long:{}".format(coords[1], coords[0]['lat'], coords[0]['lng']))

    if message.content.startswith("!insult"):
        options = requests.get("http://www.foaas.com/operations", headers={"Accept": "application/json"}).json()
        choice = options[random.randint(0, len(options)-1)]["url"]
        ask = []
        if choice == '/version':
            choice = options[random.randint(0, len(options) - 1)]["url"]
        if ":name" in choice:
            ask.append("name")
        if ":from" in choice:
            ask.append("from")
        if ":noun" in choice:
            ask.append("noun")
        if ":company" in choice:
            ask.append("company")
        if ":reference" in choice:
            ask.append("reference")
        if ":tool" in choice:
            ask.append("tool")
        if ":do" in choice:
            ask.append("do")
        if ":something" in choice:
            ask.append("something")
        if ":reaction" in choice:
            ask.append("reaction")
        if ":thing" in choice:
            ask.append("thing")
        if ":language" in choice:
            ask.append("language")
        msg = """The following variables are needed:\n"""
        for item in ask:
            msg += "{}\n".format(item)
        msg += "Please send these in your next message separated by spaces you'll have 8s to do so"
        await client.send_message(message.channel, msg)
        response = await client.wait_for_message(timeout=8, author=message.author)

        variables = response.content.split(" ")
        for needed, provided in zip(ask, variables):
            choice = choice.replace(':'+needed, provided)

        resp = requests.get("http://www.foaas.com{}".format(choice), headers={"Accept": "application/json"}).json()
        await client.send_message(message.channel, "{}\n{}".format(resp['message'], resp['subtitle']))

    if message.content.startswith("!urban"):
        word = message.content.split("!urban ")[1].replace(" ", "%20")
        url = "http://api.urbandictionary.com/v0/define"
        response = requests.get(url, params=[("term", word)]).json()
        if len(response["list"]) == 0:
            await client.send_message(message.channel, "Could not find word!")
        else:
            tags = "Related Tags:\n" + ', '.join(response["tags"])
            output = """Word:{}\nTop Definition:{}\nExample:{}\Related Tags:\n{}""".format(word, response["list"][0]["definition"], response["list"][0]["example"], tags)
            await client.send_message(message.channel, output)


def game(UserChoice):
    options = ["scissors", "paper", "rock"]
    choice = options[random.randint(0, 2)]

    UserChoice = UserChoice.lower()

    if UserChoice == 'scissors' and choice == 'paper':
        return ["You win", choice]
    elif UserChoice == 'paper' and choice == 'rock':
        return ["You win", choice]
    elif UserChoice == 'rock' and choice == 'scissors':
        return ["You win", choice]
    elif UserChoice == choice:
        return ["Draw", choice]
    else:
        return ["You Loose", choice]


def getJokes():
    global jokes
    with open("jokes.txt", 'r') as f:
        jokes = list(f.readlines())


def pickupParse():
    global pickupLines
    with open("pickup.txt", 'r') as f:
        pickupLines = list(f.readlines())


def saveIdeas(message):
        logger('--Saving Idea--')
        logger("{} : {}".format(message.author, message.content.strip("!request")))
        try:
            cur.execute("INSERT INTO ideas (idea_user, idea_desc) VALUES ('{}:{}', '{}');".format(message.server, message.author, message.content.strip("!request")))
        except (Exception, psycopg2.DatabaseError) as error:
            logger(error)
        logger('--Done Saving--')
        try:
            logger('Sending Ideas Email')
            my_address = os.environ.get("email")
            password = os.environ.get("password")
            sendTo = os.environ.get("sendTo")
            s = smtplib.SMTP(host='smtp.gmail.com', port=587)
            s.starttls()
            s.login(my_address, password)
            logger('Signed Into email')
            message = "{}:{}\n{}".format(message.server, message.author, message.content.strip("!request"))
            msg = MIMEMultipart()
            msg['From'] = my_address
            msg['To'] = sendTo
            msg['Subject'] = "Discord Idea"
            msg.attach(MIMEText(message, 'plain'))
            s.send_message(msg)
            s.quit()
            logger("Sent Ideas Email")
            return True
        except Exception as e:
            logger(e)


def getCoords(address):
    address = address.replace(' ', '+')
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}'.format(address), headers={"Key": googleToken})
    resp_json_payload = response.json()
    logger(address)
    logger(resp_json_payload['results'][0]['geometry']['location'])
    return [resp_json_payload['results'][0]['geometry']['location'], resp_json_payload['results'][0]['formatted_address']]


def logger(msg):
    now = datetime.datetime.now()
    time = "{}".format(now.strftime("%H:%M : %d-%m-%Y"))
    print("{} -- {}".format(time, msg))
    try:
        cur.execute("INSERT INTO log (log_time, log_desc) VALUES (NOW(),'{}');".format(msg))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


token = os.environ.get('BOT_TOKEN')
username = os.environ.get('User')
password = os.environ.get('Pass')
client.login(username, password)
client.run(token)
client.close()
