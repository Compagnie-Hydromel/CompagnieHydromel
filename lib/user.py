from lib.databaseConnect import querySelect, queryInsert

def getBalance(id):
    return querySelect("SELECT balance FROM users WHERE discordId = '"+str(id)+"';")[0][0]

def getUserInfo(id):
    return querySelect("SELECT users.level,users.point,wallpapers.name FROM users INNER JOIN wallpapers ON users.wallpapersId = wallpapers.id WHERE discordId = '"+str(id)+"';")[0]

def addBalance(id, balance):
    queryInsert("UPDATE users SET balance = balance+"+str(balance)+" WHERE discordId = '"+str(id)+"';")

def removeBalance(id, balance):
    if int(querySelect("SELECT balance FROM users WHERE discordId = '"+str(id)+"';")[0][0])-int(balance) >= 0:
        queryInsert("UPDATE users SET balance = balance-"+str(balance)+" WHERE discordId = '"+str(id)+"';")
        return True
    else:
        return False

def buy(buyerId,sellerId,price):
    if removeBalance(buyerId,int(price)):
        addBalance(sellerId,int(price))
        return True
    else:
        return False

def addUserIfNotExist(id):
    if not querySelect("SELECT discordId FROM users WHERE discordId = '"+str(id)+"';"):
        queryInsert("INSERT INTO users(discordId) VALUES ('"+str(id)+"');")
        userId = querySelect("SELECT id FROM users WHERE discordId = '"+str(id)+"';")[0][0]
        queryInsert("INSERT INTO usersBuyWallpapers(usersId, wallpapersId) VALUES ("+str(userId)+",1);")

def addPoint(id,point=1):
    tempPoint,level = querySelect("SELECT point, level FROM users WHERE discordId = '"+str(id)+"';")[0]
    retrn = False

    for i in range(0,point):
        tempPoint += 1
        if tempPoint >= 200*level:
            tempPoint = 0
            level += 1
            retrn = True
            addBalance(id,100+(level*100))
            wallpaper = querySelect("SELECT id,name,level FROM wallpapers WHERE level = "+str(level)+";")
            for i in wallpaper:
                idInDb = querySelect("SELECT id FROM users WHERE discordId = "+str(id)+";")[0][0]
                queryInsert("INSERT INTO usersBuyWallpapers(usersId, wallpapersId) VALUES ("+str(idInDb)+", "+str(i[0])+");")

    queryInsert("UPDATE users SET point = "+str(tempPoint)+",level = "+str(level)+" WHERE discordId = '"+str(id)+"';")

    return retrn

def removePoint(id,point=1):
    tempPoint,level = querySelect("SELECT point, level FROM users WHERE discordId = '"+str(id)+"';")[0]

    for i in range(0,point):
        tempPoint -= 1
        if tempPoint <= 0:
            if level > 1:
                level -= 1
                tempPoint = (level*200)-1
            else:
                return False

    queryInsert("UPDATE users SET point = "+str(tempPoint)+",level = "+str(level)+" WHERE discordId = '"+str(id)+"';")

    return True

def getWallpaper(wallpaper):
    try:
        return querySelect("SELECT name,level,price FROM wallpapers WHERE name = '"+str(wallpaper)+"'")[0]
    except Exception as e:
        return False

def getAllWallpaper():
    list = querySelect("SELECT name, wallpapers.level, wallpapers.price FROM wallpapers;")
    listClean = {}

    for i in list:
        listClean[i[0]] = {}
        listClean[i[0]]["level"] = i[1]
        listClean[i[0]]["price"] = i[2]

    return listClean

def getUserBuyWallpaper(id):
    list = querySelect("SELECT name, wallpapers.level, wallpapers.price FROM usersBuyWallpapers INNER JOIN users ON usersBuyWallpapers.usersId = users.id INNER JOIN wallpapers ON usersBuyWallpapers.wallpapersId = wallpapers.id WHERE discordId = '"+str(id)+"';")
    listClean = {}

    for i in list:
        listClean[i[0]] = {}
        listClean[i[0]]["level"] = i[1]
        listClean[i[0]]["price"] = i[2]

    return listClean

def changeWallpaper(id,wallpaper):
    wallpapersId = querySelect("SELECT id FROM wallpapers WHERE name = '"+str(wallpaper)+"';")[0][0]
    queryInsert("UPDATE users SET wallpapersId = "+str(wallpapersId)+" WHERE discordId = '"+str(id)+"';")

def buyWallpaper(id,wallpaper):
    wallpapersId = querySelect("SELECT id FROM wallpapers WHERE name = '"+str(wallpaper)+"';")[0][0]
    userId = querySelect("SELECT id FROM users WHERE discordId = '"+str(id)+"';")[0][0]

    queryInsert("INSERT INTO usersBuyWallpapers(usersId, wallpapersId) VALUES ("+str(userId)+", "+str(wallpapersId)+");")

def addWallpaper(wallpaper, lvlPriceSwitch="price", number=0):
    level = 0
    price = 0
    if lvlPriceSwitch == "level":
        level = number
    elif lvlPriceSwitch == "price":
        price = number

    queryInsert("INSERT INTO wallpapers(name, level, price) VALUES ('"+str(wallpaper)+"', "+str(level)+", "+str(price)+");")

def removeWallpaper(wallpaper):
    try:
        queryInsert("DELETE FROM wallpapers WHERE name = '"+str(wallpaper)+"'")
        return True
    except Exception as e:
        return False

def getBadgeList(userDiscordId):
    try:
        userId = querySelect("SELECT id FROM users WHERE discordId = '"+str(userDiscordId)+"';")[0][0]
        badgeList = querySelect("SELECT badges.name FROM usersHaveBadge INNER JOIN badges ON usersHaveBadge.badgesId = badges.id WHERE usersHaveBadge.usersId = "+str(userId)+";")

        badgeListReIndex = []
        for i in badgeList:
            badgeListReIndex.append(i[0])

        return badgeListReIndex
    except Exception as e:
        return []
