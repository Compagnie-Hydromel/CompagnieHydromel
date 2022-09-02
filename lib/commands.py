from lib.databaseConnect import querySelect, queryInsert

def getCommands(botId,root=False):
    commands = querySelect("SELECT id, name, cmdToExecute, description, hide, privateMessage FROM commands WHERE rootCommands = "+str(int(root))+" AND botId = "+str(botId))

    valueToReturn = {}

    for command in commands:
        channels = []
        for channel in querySelect("SELECT discordChannelId FROM channelToSend"):
            channels.append(channel[0])
        if bool(command[5]):
            channels.append("dm")
        valueToReturn[command[1]] = {"cmd": command[2], "description": command[3], "perm": channels, "hide": bool(command[4])}

    return valueToReturn

def getBotInfo(botId):
    return querySelect("SELECT name,discordToken FROM bot WHERE id = "+str(botId))[0]

def getAllRoot():
    queryResult = querySelect("SELECT discordId FROM users WHERE isRoot = 1")
    listOfRoot = []

    for discordId in queryResult:
        listOfRoot.append(discordId[0])

    return listOfRoot
