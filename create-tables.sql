set foreign_key_checks = 0;
DROP TABLE IF EXISTS Playlist;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS TracksInPlaylist;
set foreign_key_checks = 1;


CREATE TABLE Playlist (
	number INT NOT NULL AUTO_INCREMENT,
	playlistId VARCHAR(40) NOT NULL,
	userId VARCHAR(100) NOT NULL,
	title VARCHAR(512),
	lastUpdated DATETIME,

	PRIMARY KEY (number)
)ENGINE=InnoDB;
-- test to add a playlist
INSERT INTO Playlist(playlistId,userId,title,lastUpdated) VALUES ('7zWUZbseTIPylea5lPVtcM','b210273', 'testPlaylistTitle','2038-01-19 03:14:07');
-- spotify:user:b210273:playlist:7zWUZbseTIPylea5lPVtcM

CREATE TABLE Track(
	trackId VARCHAR(40) NOT NULL,
	duration INT NOT NULL,
	popularity INT NOT NULL,

	PRIMARY KEY (trackId)
)ENGINE=InnoDB;

# Test to add a Track
INSERT INTO Track(trackId,duration,popularity) VALUES ('6TJmQnO44YE5BtTxH8pop1','222075','0');

CREATE TABLE TracksInPlaylist(
	trackId VARCHAR(40) NOT NULL,
	playlistNumber INT NOT NULL,
	dateAdded DATETIME NOT NULL,
	dateRemoved DATETIME,

	PRIMARY KEY (trackId,playlistNumber,dateAdded),
	FOREIGN KEY (playlistNumber) REFERENCES Playlist(number),
	FOREIGN KEY (trackId) REFERENCES Track(trackId)
)ENGINE=InnoDB;
# Test to add a Track to a playlist
INSERT INTO TracksInPlaylist(trackId,playlistNumber,dateAdded) VALUES ('6TJmQnO44YE5BtTxH8pop1',1,'2012-01-19 03:14:07');

CREATE TABLE spotifyCrawler.OAuth
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    accessToken VARCHAR(100) NOT NULL,
    refreshToken VARCHAR(100) NOT NULL,
    expires DATETIME NOT NULL
);

