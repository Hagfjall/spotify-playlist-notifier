set foreign_key_checks = 0;
DROP TABLE IF EXISTS Playlist;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS TracksInPlaylist;
DROP TABLE IF EXISTS OAuth;
DROP TABLE IF EXISTS Subscriber;
DROP TABLE IF EXISTS SpotifyId;
set foreign_key_checks = 1;

CREATE TABLE `Playlist` (
  `number` int(11) NOT NULL AUTO_INCREMENT,
  `playlistId` varchar(40) NOT NULL,
  `userId` varchar(100) NOT NULL,
  `title` varchar(512) DEFAULT NULL,
  `lastUpdated` datetime DEFAULT NULL,
  `OAuthId` int(11) DEFAULT NULL,
  `snapshotId` varchar(100) DEFAULT NULL,
  `lastChanged` datetime NOT NULL,
  PRIMARY KEY (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1
#  test to add a playlist
-- INSERT INTO Playlist(playlistId,userId,title,lastUpdated) VALUES ('7zWUZbseTIPylea5lPVtcM','b210273', 'testPlaylistTitle','2038-01-19 03:14:07');
-- spotify:user:b210273:playlist:7zWUZbseTIPylea5lPVtcM

CREATE TABLE `Track` (
  `trackId` varchar(40) NOT NULL,
  `duration` int(11) NOT NULL,
  `popularity` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `artists` varchar(100) NOT NULL,
  PRIMARY KEY (`trackId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1

# Test to add a Track
-- INSERT INTO Track(trackId,duration,popularity) VALUES ('6TJmQnO44YE5BtTxH8pop1','222075','0');

CREATE TABLE `TracksInPlaylist` (
  `trackId` varchar(40) NOT NULL,
  `playlistNumber` int(11) NOT NULL,
  `dateAdded` datetime NOT NULL,
  `dateRemoved` date DEFAULT NULL,
  `addedBy` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`trackId`,`playlistNumber`,`dateAdded`,`addedBy`),
  KEY `playlistNumber` (`playlistNumber`),
  CONSTRAINT `TracksInPlaylist_ibfk_1` FOREIGN KEY (`playlistNumber`) REFERENCES `Playlist` (`number`),
  CONSTRAINT `TracksInPlaylist_ibfk_2` FOREIGN KEY (`trackId`) REFERENCES `Track` (`trackId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
# Test to add a Track to a playlist
-- INSERT INTO TracksInPlaylist(trackId,playlistNumber,dateAdded) VALUES ('6TJmQnO44YE5BtTxH8pop1',1,'2012-01-19 03:14:07');

CREATE TABLE `OAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accessToken` varchar(300) DEFAULT NULL,
  `refreshToken` varchar(300) DEFAULT NULL,
  `expires` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1

CREATE TABLE `SpotifyId` (
  `id` varchar(100) NOT NULL,
  `displayName` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1

CREATE TABLE `Subscriber` (
  `email` varchar(100) NOT NULL,
  `playlistNumber` int(11) NOT NULL,
  `lastNotified` datetime DEFAULT NULL,
  PRIMARY KEY (`email`,`playlistNumber`),
  KEY `Subscriber_ibfk_1` (`playlistNumber`),
  CONSTRAINT `Subscriber_ibfk_1` FOREIGN KEY (`playlistNumber`) REFERENCES `Playlist` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
