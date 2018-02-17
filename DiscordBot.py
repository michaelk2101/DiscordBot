import discord
import random
import datetime
import requests
import os

counter = 0
client = discord.Client()
congrats = ['Congrats', 'congrats', 'Congratulations', 'congratulations', 'Congratulation', 'congratulation']
channelToId = {'general': '409164584008548354', 'botIdea': '414063833217237002', 'botControl': '409193276885958659', 'tts': '414011036505604096'}
jokes = []
pickupLines = []


helpMenu = """-----HELP-----
!SPR   - Scissors Paper Rock -- Usage: !SPR choice
!guess - guess a number between 1 and 10 
!ping  - pong
!joke  - these are offensive you have been warned
!flirt - flirt with a bot - you lonely bastard 
!coords- get coordinates of an address
!insult    - insult someone
-----END-----
"""


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("--------")


@client.event
async def on_member_join(member):
    await client.send_message(client.get_channel(channelToId['general']), "Welcome bitch!")
    print(member)
    

@client.event
async def on_message(message):
    global counter
    counter += 1
    saveIdeas(message)

    now = datetime.datetime.now()
    print("{} -- {} -- {} : {}".format(now.strftime("%H:%M : %d-%m-%Y"), message.author, message.channel, message.content))
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

    if 'gucci' in message.content or 'Gucci' in message.content:
        await client.send_message(message.channel, 'Kill Your Self :rage:')

    if 'haha' in message.content:
        await client.send_message(message.channel, ':joy:')

    if 'bot' in message.content:
        typeOfMessage = random.randint(0, 1)
        if typeOfMessage:
            await client.send_message(message.channel, 'Someone say bot!')
            resp = await client.wait_for_message(timeout=5)
            if 'no' in resp.content or 'No' in resp.content:
                await client.send_message(message.channel, "Fk You!")
        else:
            await client.send_message(message.channel, "What!")

    # Functions/ commands

    if message.content.startswith("!help"):
        await client.send_message(message.channel, helpMenu)

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

    if message.content.startswith("!SPR"):
        userChoice = message.content.split(" ")[1]
        result = game(userChoice)
        msg = "I chose {} you choose {}\n{}".format(result[1], userChoice, result[0])
        await client.send_message(message.channel, msg)

    if message.content.startswith("!coords"):
        address = message.content.replace("!coords",'')
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
    print(message.channel)
    if message.channel == client.get_channel(channelToId['botIdea']):
        print('--Saving Idea--')
        now = datetime.datetime.now()
        with open("ideas.txt", 'w') as f:
            f.write("{} -- {} : {}".format(now.strftime("%H:%M : %d-%m-%Y"), message.author, message.content))
        print('--Done Saving--')


def getCoords(address):
    address = address.replace(' ', '+')
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}'.format(address), headers={"Key": "AIzaSyDSDzf7Haov89VXJXquoRg3g08FQ_a0RTI"})
    resp_json_payload = response.json()
    print(address)
    print(resp_json_payload['results'][0]['geometry']['location'])
    return [resp_json_payload['results'][0]['geometry']['location'], resp_json_payload['results'][0]['formatted_address']]


token = os.environ['BOT_TOKEN']
client.run(token)
client.close()

