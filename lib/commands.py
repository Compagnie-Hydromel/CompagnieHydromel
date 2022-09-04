from lib.databaseConnect import querySelect, queryInsert

def getCommands(botId,root=False,all=False):
    query = "SELECT id, name, cmdToExecute, description, hide, privateMessage FROM commands WHERE rootCommands = "+str(int(root))+" AND botId = "+str(botId)
    if all:
        query = "SELECT id, name, cmdToExecute, description, hide, privateMessage FROM commands"

    commands = querySelect(query)

    valueToReturn = {}

    for command in commands:
        channels = []
        for channel in querySelect("SELECT discordChannelId FROM channelToSend WHERE commandsId = "+str(command[0])):
            channels.append(int(channel[0]))
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

def setRoot(discordId,isRoot=True):
    if not "'" in discordId and not '"' in discordId:
        queryInsert('UPDATE users SET isRoot = '+str(int(isRoot))+' WHERE discordId = "'+str(discordId)+'"')

def setDmAccess(commandsName, set=True):
    if not "'" in discordId and not '"' in discordId:
        queryInsert("UPDATE commands SET privateMessage = "+str(int(set))+" WHERE name = '"+str(commandsName)+"';")

def addCommandsPermissionInChannels():
    queryInsert("INSERT INTO ")
