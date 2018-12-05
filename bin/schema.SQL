
-- DROP TABLE IF EXISTS artists;
-- DROP TABLE IF EXISTS songs;
-- DROP TABLE IF EXISTS connections;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS song_features;


-- CREATE TABLE artists (
--   id                    SERIAL PRIMARY KEY NOT NULL,
--   name                  VARCHAR,
--   url                   VARCHAR,
--   scraped               INTEGER,
--   scraped_spotify       INTEGER
-- );

-- CREATE TABLE songs (
--   id                    SERIAL PRIMARY KEY NOT NULL,
--   artist_id             INTEGER,
--   name                  VARCHAR,
--   corrected_name        VARCHAR,
--   url                   VARCHAR,
--   scraped               INTEGER,
--   scraped_spotify       INTEGER
-- );

-- CREATE TABLE connections (
--   song_id               INTEGER,
--   sampled_by_song_id    INTEGER,
--   is_connected          INTEGER
-- );

CREATE TABLE predictions (
  user_song_id          INTEGER,
  item_song_id          INTEGER,
  user_song_name        VARCHAR,
  user_song_artist      VARCHAR,
  item_song_name        VARCHAR,
  item_song_artist      VARCHAR,
  rating                INTEGER
);


CREATE TABLE song_features (
  id                    INTEGER,
  danceability          NUMERIC,
  energy                NUMERIC,
  song_key              INTEGER,
  loudness              NUMERIC,
  mode                  INTEGER,
  speechiness           NUMERIC,
  acousticness          NUMERIC,
  instrumentalness      NUMERIC,
  liveness              NUMERIC,
  valence               NUMERIC,
  tempo                 NUMERIC,
  spotify_id            VARCHAR,      
  uri                   VARCHAR,
  track_href            VARCHAR,
  analysis_url          VARCHAR,
  duration_ms           INTEGER,
  time_signature        INTEGER
);
