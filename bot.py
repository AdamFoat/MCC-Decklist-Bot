import discord
from discord.ext import commands
import base64
import numpy as np
import PIL
from PIL import Image
import urllib.request
from natsort import natsorted

client = commands.Bot(command_prefix="#")

TOKEN = "ODA2NjMwODQ5MDA0NTY4NTk3.YBsPhA.CSqCy3d9pWKPOpFq6f2dqWP7a5M"

@client.event
async def onready():
    print("Bot is Ready")

@client.command()
async def test(ctx):
    await ctx.send("working")

@client.command()
async def deckcode(ctx, *deck):
    filelist = list(deck)
    filelist = natsorted(filelist)  # sort cards into alphanumeric order
    listofsets = []  # create a list of what sets each card is in
    for card in filelist:
        cardset = card[0] + card[1]
        listofsets.append(cardset)
    listofcountedsets = natsorted([[x, listofsets.count(x)] for x in set(listofsets)])

    setdata = []
    for sublist in listofcountedsets:
        for item in sublist:
            setdata.append(str(item))

    listofcardnumbers = []  # create a list of the card number for each set
    for card in filelist:
        cardnumber = card[3:]
        if len(cardnumber) < 3:  # pad numbers with 2 or less digits so they remain equal size when encoded
            cardnumber = "0" + cardnumber
        listofcardnumbers.append(cardnumber)

    deckdata = setdata + listofcardnumbers  # add both lists of deck information together
    deckdata = "".join(deckdata)  # turn list into a string
    setinfo = deckdata[:-75]
    numberinfo = deckdata[-75:]

    bytelength = (int(numberinfo).bit_length() + 7) // 8
    numberinfo = int(numberinfo).to_bytes(bytelength, 'big')

    encodenumberinfo = base64.b64encode(numberinfo)
    encodenumberinfo = encodenumberinfo.decode("utf-8")

    encodeddeckdata = setinfo + "@" + encodenumberinfo
    await ctx.send(encodeddeckdata)

@client.command()
async def showdeck(ctx, arg):
    separation = int(arg.find("@"))
    setinfo = arg[:separation]
    encodednumberinfo = (arg[separation + 1:]).encode("utf-8")

    numberinfo = base64.b64decode(encodednumberinfo)
    numberinfo = str(int.from_bytes(numberinfo, 'big'))

    if len(numberinfo) == 73:
        numberinfo = "00" + numberinfo
    elif len(numberinfo) == 74:
        numberinfo = "0" + numberinfo

    deckdata = setinfo + numberinfo
    setinfo = deckdata[:-75]
    numberinfo = deckdata[-75:]
    numberinfo = [numberinfo[i:i + 3] for i in range(0, len(numberinfo), 3)]
    listofconvertednumbers = []
    for card in numberinfo:
        if card[0] == "0":
            listofconvertednumbers.append(card[1:])
        else:
            listofconvertednumbers.append(card)

    listofsetsused = []
    listofnumberofcardsperset = []
    position = 0
    while position != len(setinfo):
        if setinfo[position].isalpha():
            listofsetsused.append(setinfo[position] + setinfo[position + 1])
            position += 2
        else:
            if position + 2 > len(setinfo):
                listofnumberofcardsperset.append(setinfo[position])
                position += 1
            elif setinfo[position + 1].isnumeric():
                listofnumberofcardsperset.append(setinfo[position] + setinfo[position + 1])
                position += 2
            else:
                listofnumberofcardsperset.append(setinfo[position])
                position += 1

    setposition = 0
    listofcardsindeck = []
    while setposition != len(listofsetsused):
        cardsinset = listofconvertednumbers[0:int(listofnumberofcardsperset[setposition])]
        completedcards = [listofsetsused[setposition] + "-" + card for card in cardsinset]
        listofconvertednumbers = listofconvertednumbers[int(listofnumberofcardsperset[setposition]):]
        listofcardsindeck += completedcards
        setposition += 1

    cardlibrary = {}
    with open(r"C:\Users\GFOAT\PycharmProjects\MCC Decklist Bot\Card Library.txt") as f:
        for line in f:
            (key, val) = line.split("@")
            cardlibrary[key] = val
    decklist = []
    imagelist = []
    for card in listofcardsindeck:
        splitinfo = (cardlibrary.get(card)).split("$")
        decklist.append(splitinfo[0] + "\n")
        imagelist.append((splitinfo[1]).replace("\n", ""))
    deckfile = open("Your Decklist.txt", "w")
    deckfile.write("Deck Code = " + arg + "\n")
    for card in decklist:
        deckfile.write(card)
    deckfile.close()
    await ctx.send(file=discord.File(r"C:\Users\GFOAT\PycharmProjects\MCC Decklist Bot\Your Decklist.txt"))
    await ctx.send("Creating deck image, this may take a few moments")
    n = 1
    for image in imagelist:
        urllib.request.urlretrieve(image, str(n) + ".png")
        n += 1
    imagelist = []
    for i in range(1, 26):
        imagelist.append(str(i) + ".png")
    imagelist = [PIL.Image.open(i) for i in imagelist]
    imagerow1 = imagelist[0:5]
    min_shape1 = sorted([(np.sum(i.size), i.size) for i in imagerow1])[0][1]
    images_comb1 = np.hstack((np.asarray(i.resize(min_shape1)) for i in imagerow1))
    images_comb1 = PIL.Image.fromarray(images_comb1)
    images_comb1.save("row1.png")
    imagerow2 = imagelist[5:10]
    min_shape2 = sorted([(np.sum(i.size), i.size) for i in imagerow2])[0][1]
    images_comb2 = np.hstack((np.asarray(i.resize(min_shape2)) for i in imagerow2))
    images_comb2 = PIL.Image.fromarray(images_comb2)
    images_comb2.save("row2.png")
    imagerow3 = imagelist[10:15]
    min_shape3 = sorted([(np.sum(i.size), i.size) for i in imagerow3])[0][1]
    images_comb3 = np.hstack((np.asarray(i.resize(min_shape3)) for i in imagerow3))
    images_comb3 = PIL.Image.fromarray(images_comb3)
    images_comb3.save("row3.png")
    imagerow4 = imagelist[15:20]
    min_shape4 = sorted([(np.sum(i.size), i.size) for i in imagerow4])[0][1]
    images_comb4 = np.hstack((np.asarray(i.resize(min_shape4)) for i in imagerow4))
    images_comb4 = PIL.Image.fromarray(images_comb4)
    images_comb4.save("row4.png")
    imagerow5 = imagelist[20:25]
    min_shape5 = sorted([(np.sum(i.size), i.size) for i in imagerow5])[0][1]
    images_comb5 = np.hstack((np.asarray(i.resize(min_shape5)) for i in imagerow5))
    images_comb5 = PIL.Image.fromarray(images_comb5)
    images_comb5.save("row5.png")
    verticalimages = ["row1.png","row2.png","row3.png","row4.png","row5.png"]
    verticalimages = [PIL.Image.open(i) for i in verticalimages]
    min_shapevertic = (1000, 200)
    imagescombinedfinal = np.vstack((np.asarray(i.resize(min_shapevertic)) for i in verticalimages))
    imgs_comb = PIL.Image.fromarray(imagescombinedfinal)
    imgs_comb.save("DeckImage.png")

    await ctx.send(file=discord.File(r"C:\Users\GFOAT\PycharmProjects\MCC Decklist Bot\DeckImage.png"))

client.run(TOKEN)