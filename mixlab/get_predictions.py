#!/usr/bin/env python3

import database_interaction
import model

def get_and_write_predictions():
    sr = model.SongRecommender(itemCol='song_id',
                     userCol='sampled_by_song_id',
                     ratingCol='is_connected',
                     nonnegative=True,
                     regParam=0.01,
                     rank=100,
                     alpha=30,
                     implicitPrefs=True)


    db = database_interaction.DatabaseInteraction(db_name='mixmaker')
    
    print('Getting data...')
    df = db.get_table('connections')
    data = sr.spark.createDataFrame(df)

    print('Fitting model...')
    recommender = sr.fit(data)

    print('Getting predictions...')
    preds = sr.get_predictions_for_all_users(df, recommender, n_predictions=10)
    
    print('Writing predictions...')
    db.write_predictions(preds, 'predictions_temp')


# get_and_write_predictions()













