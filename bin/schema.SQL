
DROP TABLE IF EXISTS artist_urls;


CREATE TABLE artists(
  artist_id serial      PRIMARY KEY NOT NULL,
  name                  VARCHAR,
  artist_urls           VARCHAR,

);

