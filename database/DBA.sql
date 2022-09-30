-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Linux
-- HeidiSQL Version:             12.0.0.6468
-- --------------------------------------------------------

-- Dumping database structure for CompagnieHydromel
CREATE DATABASE IF NOT EXISTS CompagnieHydromel;
USE CompagnieHydromel;

-- Dumping structure for table CompagnieHydromel.badges
CREATE TABLE IF NOT EXISTS `badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
);

-- Dumping structure for table CompagnieHydromel.bot
CREATE TABLE IF NOT EXISTS `bot` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `discordToken` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `file` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
);

-- Dumping structure for table CompagnieHydromel.commands
CREATE TABLE IF NOT EXISTS `commands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `cmdToExecute` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `hide` tinyint DEFAULT '0',
  `botId` int NOT NULL,
  `privateMessage` tinyint DEFAULT '0',
  `rootCommands` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `FK_BotId` (`botId`),
  CONSTRAINT `FK_BotId` FOREIGN KEY (`botId`) REFERENCES `bot` (`id`)
);

-- Dumping structure for table CompagnieHydromel.channelToSend
CREATE TABLE IF NOT EXISTS `channelToSend` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commandsId` int NOT NULL,
  `discordChannelId` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UCcommandsChannel` (`commandsId`,`discordChannelId`),
  CONSTRAINT `FK_CommandsId` FOREIGN KEY (`commandsId`) REFERENCES `commands` (`id`)
);

-- Dumping structure for table CompagnieHydromel.wallpapers
CREATE TABLE IF NOT EXISTS `wallpapers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `level` int NOT NULL,
  `price` int NOT NULL,
  PRIMARY KEY (`id`)
);

-- Dumping structure for table CompagnieHydromel.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discordId` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `point` int NOT NULL DEFAULT '1',
  `level` int NOT NULL DEFAULT '1',
  `balance` int NOT NULL DEFAULT '20',
  `wallpapersId` int NOT NULL DEFAULT '1',
  `isRoot` tinyint DEFAULT '0',
  `barColor` varchar(8) COLLATE utf8mb4_general_ci DEFAULT 'ADFF2F',
  `nameColor` varchar(8) COLLATE utf8mb4_general_ci DEFAULT '0000FF',
  `numberOfbuy` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Column 2` (`discordId`),
  KEY `wallpapersID` (`wallpapersId`) USING BTREE,
  CONSTRAINT `wallpaperId` FOREIGN KEY (`wallpapersId`) REFERENCES `wallpapers` (`id`)
);

-- Dumping structure for table CompagnieHydromel.usersBuyWallpapers
CREATE TABLE IF NOT EXISTS `usersBuyWallpapers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usersId` int NOT NULL,
  `wallpapersId` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wallpapersId` (`wallpapersId`),
  KEY `userId` (`usersId`) USING BTREE,
  CONSTRAINT `buyWallpaperId` FOREIGN KEY (`wallpapersId`) REFERENCES `wallpapers` (`id`),
  CONSTRAINT `userId2` FOREIGN KEY (`usersId`) REFERENCES `users` (`id`)
);

-- Dumping structure for table CompagnieHydromel.usersHaveBadge
CREATE TABLE IF NOT EXISTS `usersHaveBadge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usersId` int NOT NULL,
  `badgesId` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `userId` (`usersId`) USING BTREE,
  KEY `badgeIf` (`badgesId`) USING BTREE,
  CONSTRAINT `badgeId` FOREIGN KEY (`badgesId`) REFERENCES `badges` (`id`),
  CONSTRAINT `userId` FOREIGN KEY (`usersId`) REFERENCES `users` (`id`)
);

-- Dumping data for table CompagnieHydromel.bot: ~3 rows (approximately)
INSERT INTO `bot` (`id`, `name`, `discordToken`, `file`) VALUES
	(1, 'GeorgeLeBarman', '', 'Barman.py'),
	(2, 'JouskierLeMenestrel', '', 'Menestrel.py'),
	(3, 'IsabelialArchiveuse', '', 'Archiveuse.py');

-- Dumping data for table CompagnieHydromel.commands: ~26 rows (approximately)
INSERT INTO `commands` (`id`, `name`, `cmdToExecute`, `description`, `hide`, `botId`, `privateMessage`, `rootCommands`) VALUES
	(1, 'help', 'help(message,argument)', 'Simple Help page', 0, 1, 1, 0),
	(3, 'biere', 'buyFromGeorge(message,argument,\'Ptit biere (Attention 5$ la biere)\',\'img/biere\',5)', 'Pour te servir une belle bire', 0, 1, 0, 0),
	(5, 'hydromel', 'buyFromGeorge(message,argument,\'Pour les vrai ;) (Attention 7$ le verre d\'hydromel des dieux)\',\'img/Hydromel1.jpg\',7)', 'Pour te servir un verre d\'hydromel', 0, 1, 0, 0),
	(6, 'water', 'buyFromGeorge(message,argument,\'Pour les faibles (Attention 1$ le verre d\\\'eau)\',\'img/water.jpg\',1)', 'Pour te servir un verre d\'eau pour les faibles', 0, 1, 0, 0),
	(7, 'verresansalcool', 'buyFromGeorge(message,argument,\'Ptit verre sans alcool (Attention 3$ le verre)\',\'img/verre\',3)', 'Pour te servir un verre sans alcool de faible', 0, 1, 0, 0),
	(8, 'caveDeTorture', 'caveDeTorture(message,argument)', '...', 1, 1, 1, 0),
	(9, 'hentai', 'SendMessage(message,argument,\'\',\'img/hentai/\')', 'Pour avoir des photos de hentai', 0, 1, 1, 0),
	(10, 'porn', 'SendMessage(message,argument, \'\', \'img/porn/\')', 'Pour avoir des photos pornographiques', 0, 1, 1, 0),
	(11, 'jinx', 'SendMessage(message,argument,\'\',\'img/jinx/\')', 'Pour avoir des photos de Jinx ;)', 0, 1, 1, 0),
	(12, '002', 'SendMessage(message,argument,\'\',\'img/002/\')', 'Pour avoir des photos Zero Two', 0, 1, 1, 0),
	(13, 'shitpost', 'SendMessage(message,argument,getImageReddit(\'shitposting\').url)', 'Pour envoyer du shitpost', 0, 1, 1, 0),
	(14, 'meme', 'SendMessage(message,argument,getImageReddit(\'meme\').url)', 'Pour envoyer un meme', 0, 1, 1, 0),
	(15, 'pierrot', 'SendMessage(message,argument,\'\', \'img/pierrot/\')', 'Pour envoyer un pierrot', 1, 1, 0, 0),
	(16, 'bar', 'SendMessage(message,argument,\'\', getBarImage())', 'Affiche le bar avec les gens assis', 0, 1, 1, 0),
	(17, 'profil', 'show(message,argument)', 'Simple show profil page', 0, 3, 1, 0),
	(18, 'balance', 'balance(message,argument)', 'See you\'re money', 0, 3, 1, 0),
	(19, 'play', 'play(message,argument)', 'play Music', 0, 2, 0, 0),
	(20, 'skip', 'skip(message,argument)', 'skip Music', 0, 2, 0, 0),
	(21, 'stop', 'stop(message,argument)', 'stop Music', 0, 2, 0, 0),
	(22, 'lock', 'actLock(message,argument)', 'Activer la lock pour le non root a l\'accs du bot au salon musique', 1, 2, 0, 1),
	(24, 'clear', 'clear(message,argument)', 'Pour clear tout les messages d\'un salon textuelle', 0, 1, 0, 1),
	(26, 'channel', 'channel(message,argument)', 'Gestion des permission pour l\'accs au salon textuelle', 0, 1, 0, 1),
	(27, 'root', 'rootManage(message,argument)', 'Manage root account', 0, 1, 0, 1),
	(28, 'broadcast', 'broadcast(message,argument)', 'broadcast in a channel', 0, 1, 0, 1),
	(29, 'money', 'money(message,argument)', 'Pour ajouter de l\'argent a quelqu\'un', 0, 3, 0, 1),
	(30, 'wallpaper', 'manageWallpaper(message,argument)', 'Pour ajouter des wallpaper', 0, 3, 0, 1),
  (31, 'top', 'top(message,argument)', 'Pour voir les personne avec le plus gros level', 0, 3, 0, 0);

  INSERT INTO `wallpapers` (`id`, `name`, `level`, `price`) VALUES (1, 'default', 0, 500);
