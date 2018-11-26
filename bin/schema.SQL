
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS connections;


CREATE TABLE artists(
  id            SERIAL PRIMARY KEY NOT NULL,
  name          VARCHAR,
  url           VARCHAR
);

CREATE TABLE songs(
  id            SERIAL PRIMARY KEY NOT NULL,
  name          VARCHAR,
  url           VARCHAR
);

CREATE TABLE connections (
  song_id     integer,
  sampled_by_song_id integer
);
