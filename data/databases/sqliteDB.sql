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
  smartpoint INTEGER DEFAULT '20',
  wallpapersId INTEGER DEFAULT '1',
  isRoot INTEGER DEFAULT '0',
  barColor TEXT DEFAULT 'ADFF2F',
  nameColor TEXT DEFAULT '0000FF',
  numberOfBuy INTEGER DEFAULT '0',
  profilesLayoutId INTEGER DEFAULT '1',
  CONSTRAINT current_profiles_layout_id_foreign_key FOREIGN KEY (profilesLayoutId) REFERENCES profilesLayout (id),
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

CREATE TABLE IF NOT EXISTS profilesLayout (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  profilPictureX INTEGER NOT NULL,
  profilPictureY INTEGER NOT NULL,
  nameX INTEGER NOT NULL,
  nameY INTEGER NOT NULL,
  userNameX INTEGER NOT NULL,
  userNameY INTEGER NOT NULL,
  levelX INTEGER NOT NULL,
  levelY INTEGER NOT NULL,
  badgeX INTEGER NOT NULL,
  badgeY INTEGER NOT NULL,
  levelBarX INTEGER NOT NULL,
  levelBarY INTEGER NOT NULL
);

INSERT INTO wallpapers (id, name, url, level, price) VALUES 
(1, 'default', 'https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png', 0, 0);

INSERT INTO profilesLayout (id, name, profilPictureX, profilPictureY, nameX, nameY, userNameX, userNameY, levelX, levelY, badgeX, badgeY, levelBarX, levelBarY) VALUES 
(1, "default", 0, 0, 150, 20, 150, 65, 250, 224, 150, 90, 0, 254),
(2, "reimaginated", 186, 35, 186, 155, 190, 195, 250, 224, 150, 5, 0, 254);