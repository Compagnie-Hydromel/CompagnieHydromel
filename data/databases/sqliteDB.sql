CREATE TABLE IF NOT EXISTS badges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wallpapers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL,
  level INTEGER NOT NULL,
  price INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  discordId TEXT UNIQUE,
  point INTEGER DEFAULT '1',
  level INTEGER DEFAULT '1',
  balance INTEGER DEFAULT '20',
  wallpapersId INTEGER DEFAULT '1',
  isRoot INTEGER DEFAULT '0',
  barColor TEXT DEFAULT 'ADFF2F',
  nameColor TEXT DEFAULT '0000FF',
  numberOfbuy INTEGER DEFAULT '0',
  CONSTRAINT wallpaperId FOREIGN KEY (wallpapersId) REFERENCES wallpapers (id)
);

CREATE TABLE IF NOT EXISTS usersBuyWallpapers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usersId INTEGER NOT NULL,
  wallpapersId INTEGER NOT NULL,
  CONSTRAINT buyWallpaperId FOREIGN KEY (wallpapersId) REFERENCES wallpapers (id),
  CONSTRAINT userId2 FOREIGN KEY (usersId) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS usersHaveBadge (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usersId INTEGER NOT NULL,
  badgesId INTEGER NOT NULL,
  CONSTRAINT badgeId FOREIGN KEY (badgesId) REFERENCES badges (id),
  CONSTRAINT userId FOREIGN KEY (usersId) REFERENCES users (id)
);

INSERT INTO wallpapers (id, name, url, level, price) VALUES (1, 'default', 'https://shkermit.ch/~ethann/compHydromelWallpaper/default.png', 0, 500);
