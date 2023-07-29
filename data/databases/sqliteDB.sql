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
  smartcoin INTEGER DEFAULT '20',
  wallpapersId INTEGER DEFAULT '1',
  isRoot INTEGER DEFAULT '0',
  barColor TEXT DEFAULT 'ADFF2F',
  nameColor TEXT DEFAULT '0000FF',
  numberOfbuy INTEGER DEFAULT '0',
  CONSTRAINT current_wallpapers_id_foreign_key FOREIGN KEY (wallpapersId) REFERENCES wallpapers (id)
);

CREATE TABLE IF NOT EXISTS usersBuyWallpapers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usersId INTEGER NOT NULL,
  wallpapersId INTEGER NOT NULL,
  CONSTRAINT buy_wallpapers_id_foreign_key FOREIGN KEY (wallpapersId) REFERENCES wallpapers (id),
  CONSTRAINT users_id_foreign_key FOREIGN KEY (usersId) REFERENCES users (id),
  UNIQUE (usersId, wallpapersId)
);

CREATE TABLE IF NOT EXISTS usersHaveBadge (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usersId INTEGER NOT NULL,
  badgesId INTEGER NOT NULL,
  CONSTRAINT badges_id_foreign_key FOREIGN KEY (badgesId) REFERENCES badges (id),
  CONSTRAINT users_id_foreign_key FOREIGN KEY (usersId) REFERENCES users (id)
);

INSERT INTO wallpapers (id, name, url, level, price) VALUES 
(1, 'default', 'https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png', 0, 0);