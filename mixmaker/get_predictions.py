
from database_interaction import DatabaseInteraction
from model import SongRecommender


sr = SongRecommender(itemCol='song_id',
                     userCol='sampled_by_song_id',
                     ratingCol='is_connected',
                     nonnegative=True,
                     regParam=0.01,
                     rank=10)

db = DatabaseInteraction(db_name=mixmaker)

df = db.get_table('connections')
data = sr.spark.createDataFrame(df)
recommender = sr.fit(data)












