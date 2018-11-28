
-- DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS connections;


CREATE TABLE artists(
  id            SERIAL PRIMARY KEY NOT NULL,
  name          VARCHAR,
  url           VARCHAR,
  scraped       INTEGER
);

CREATE TABLE songs(
  id            SERIAL PRIMARY KEY NOT NULL,
  artist_id     INTEGER,
  name          VARCHAR,
  url           VARCHAR,
  scraped       INTEGER
);

CREATE TABLE connections (
  song_id               INTEGER,
  sampled_by_song_id    INTEGER,
  remixed_by_song_id    INTEGER
);
