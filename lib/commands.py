from lib.databaseConnect import querySelect, queryInsert

def getCommands(botId,root=False,all=False):
    query = "SELECT commands.id, commands.name, cmdToExecute, description, hide, privateMessage,bot.name AS bot FROM commands INNER JOIN bot ON bot.id = commands.botId WHERE rootCommands = "+str(int(root))+" AND botId = "+str(botId)
    if all:
        query = "SELECT commands.id, commands.name, cmdToExecute, description, hide, privateMessage,bot.name AS bot FROM commands INNER JOIN bot ON bot.id = commands.botId"
        if not root:
            query += " WHERE rootCommands = "+str(int(root))

    commands = querySelect(query)

    valueToReturn = {}

    for command in commands:
        channels = []
        for channel in querySelect("SELECT discordChannelId FROM channelToSend WHERE commandsId = "+str(command[0])):
            channels.append(int(channel[0]))
        if bool(command[5]):
            channels.append("dm")
        valueToReturn[command[1]] = {"cmd": command[2], "description": command[3], "perm": channels, "hide": bool(command[4]), "bot": command[6]}

    return valueToReturn

def getBotInfo(botId):
    return querySelect("SELECT name,discordToken FROM bot WHERE id = "+str(botId))[0]

def getAllRoot():
    queryResult = querySelect("SELECT discordId FROM users WHERE isRoot = 1")
    listOfRoot = []

    for discordId in queryResult:
        listOfRoot.append(str(discordId[0]))

    return listOfRoot

def setRoot(discordId,isRoot=True):
    if not "'" in discordId and not '"' in discordId:
        queryInsert('UPDATE users SET isRoot = '+str(int(isRoot))+' WHERE discordId = "'+str(discordId)+'"')

def setDmAccess(commandsName, set=True):
    queryInsert("UPDATE commands SET privateMessage = "+str(int(set))+" WHERE name = '"+str(commandsName)+"'")

def addCommandsPermissionInChannels(commandsName, channelId):
    commandsId = querySelect("SELECT id FROM commands WHERE name = '"+str(commandsName)+"'")[0][0]
    queryInsert("INSERT INTO channelToSend(commandsId,discordChannelId) VALUES ("+str(commandsId)+", "+str(channelId)+")")

def removeCommandsPermissionInChannels(commandsName, channelId):
    commandsId = querySelect("SELECT id FROM commands WHERE name = '"+str(commandsName)+"'")[0][0]
    queryInsert("DELETE FROM channelToSend WHERE commandsId = "+str(commandsId)+" AND discordChannelId = "+str(channelId))
