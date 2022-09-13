from lib.databaseConnect import querySelect, queryInsert

def getBotInfo(botId):
    return querySelect("SELECT name,discordToken FROM bot WHERE id = "+str(botId))[0]

def getBotList():
    queryResult = querySelect("SELECT name,id FROM bot")
    listOfBot = {}

    for bot in queryResult:
        listOfBot[bot[0]] = bot[1]

    return listOfBot
