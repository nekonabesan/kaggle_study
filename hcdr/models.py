import numpy as np
import pandas as pd
import xgboost as xgb
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping

import lightgbm as lgb
from lightgbm import LGBMClassifier

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


# tensorflowの警告抑制
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


# LightGBMによるモデル
class Model1Lgb:

    def __init__(self):
        self.model = None

    def fit(self, tr_x, tr_y, va_x, va_y):

        params = {
            'boosting_type': 'gbdt'
            ,'objective': 'binary'
            ,'metric': 'auc'
            ,'learning_rate': 0.02
            ,'max_bin':400
            ,'max_depth': -1
            ,'num_leaves': 30
            ,'min_child_samples': 70
            ,'subsample': 1.0
            ,'subsample_freq': 1
            ,'colsample_bytree': 0.05
            ,'min_split_gain': 0.5
            ,'reg_alpha': 0.0
            ,'reg_lambda': 100
            ,'n_estimators': 2000
        }
        
        num_round = 100
        lgb_train = lgb.Dataset(tr_x, tr_y)
        lgb_eval = lgb.Dataset(va_x, va_y)
        categorical_features = []
        self.model = lgb.train(params, lgb_train, num_boost_round=num_round,
                        categorical_feature=categorical_features,
                        valid_names=['train', 'valid'], valid_sets=[lgb_train, lgb_eval])

    def predict(self, x):
        #data = lgb.Dataset(x)
        pred = self.model.predict(x)
        return pred


# xgboostによるモデル
class Model1Xgb:

    def __init__(self):
        self.model = None

    def fit(self, tr_x, tr_y, va_x, va_y):
        params = {
            'booster': 'gbtree'
            ,'objective': 'binary:logistic'
            ,'silent': 1
            ,'random_state': 17
            ,'eval_metric': 'auc'
            ,'eta': 0.1
            ,'max_depth': 11
            ,'eta': 0.01
            ,'subsample': 0.708
            ,'colsample_state': 71
            ,'colsample_bytree': 1.0
            ,'colsample_bylevel': 0.3
            ,'gamma': 0
            ,'lambda': 4.930
            ,'alpha': 3.564
            ,'min_child_weight': 6
            ,'gpu_id': 0
            ,'tree_method': 'gpu_hist'
            ,'num_round': 1000
        }
        num_round = 1000
        dtrain = xgb.DMatrix(tr_x, label=tr_y)
        dvalid = xgb.DMatrix(va_x, label=va_y)
        watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
        self.model = xgb.train(params, dtrain, num_round, evals=watchlist)

    def predict(self, x):
        data = xgb.DMatrix(x)
        pred = self.model.predict(data)
        return pred


# ニューラルネットによるモデル
class Model1NN:

    def __init__(self):
        self.model = None
        self.scaler = None

    def fit(self, tr_x, tr_y, va_x, va_y):
        self.scaler = StandardScaler()
        self.scaler.fit(tr_x)

        batch_size = 128
        epochs = 10
        early_stopping = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

        tr_x = self.scaler.transform(tr_x)
        va_x = self.scaler.transform(va_x)
        model = Sequential()
        model.add(Dense(256, activation='relu', input_shape=(tr_x.shape[1],)))
        model.add(Dropout(0.2))
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy'
                    ,optimizer='adam'
                    ,metrics=['accuracy'])

        history = model.fit(tr_x, tr_y,
                    batch_size=batch_size
                    ,epochs=epochs
                    ,verbose=1
                    ,validation_split=0.
                    ,validation_data=(va_x, va_y)
                    ,callbacks=[early_stopping]
                    )
        self.model = model

    def predict(self, x):
        x = self.scaler.transform(x)
        pred = self.model.predict(x)
        return pred



# 線形モデル
class Model2Linear:

    def __init__(self):
        self.model = None
        self.scaler = None

    def fit(self, tr_x, tr_y, va_x, va_y):
        self.scaler = StandardScaler()
        self.scaler.fit(tr_x)
        tr_x = self.scaler.transform(tr_x)
        self.model = LogisticRegression(solver='lbfgs', C=1.0)
        self.model.fit(tr_x, tr_y)

    def predict(self, x):
        x = self.scaler.transform(x)
        pred = self.model.predict(x)[:, 1]
        return pred