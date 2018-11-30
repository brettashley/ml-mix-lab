import pandas as pd
import numpy as np
import pyspark as ps
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
import psycopg2
from pyspark.ml.recommendation import ALS
from pandas.io import sql
from sklearn.model_selection import train_test_split
from pyspark.ml.evaluation import RegressionEvaluator

class SongRecommender():

    def __init__(self,
                itemCol='song_id',
                userCol='sampled_by_song_id',
                ratingCol='is_connected',
                nonnegative=True,
                regParam=0.01,
                rank=10):

        self.itemCol = itemCol
        self.userCol = userCol
        self.ratingCol = ratingCol
        self.nonnegative = nonnegative
        self.regParam = regParam
        self.rank = rank
        self.als_model = ALS(itemCol=self.itemCol,
                            userCol=self.userCol,
                            ratingCol=self.ratingCol,
                            nonnegative=self.nonnegative,
                            regParam=self.regParam,
                            rank=self.rank)
        
    
    def fit(self, X):
        return self.als_model.fit(X)

    def transform(self, recommender, X):
        return recommender.transform(X)

    def _get_negative_targets(self, ):
        pass

    def RMSE(self, predictions, has_nan_values=False):
        evaluator = RegressionEvaluator(metricName='rmse', 
                                       labelCol=self.labelCol,
                                       predictionCol='prediction')
        if has_nan_values:
            # check for nan values by computation
            filtered_preds = predictions.filter("prediction + 1 > prediction")
            return evaluator.evaluate(filtered_preds)
        
        else:
            return evaluator.evaluate(predictions)













