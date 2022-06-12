from email.mime import application
from statistics import mode
from tracemalloc import start
import numpy as np
import pandas as pd
import math
import re
import pickle
import gc
from sklearn import metrics
import optuna
from optuna.distributions import UniformDistribution

from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sqlalchemy import null

import lightgbm as lgb
from lightgbm import LGBMClassifier
from yaml import warnings

import xgboost as xgb
from sklearn.metrics import log_loss
from xgboost.sklearn import XGBClassifier

import warnings
warnings.filterwarnings("ignore")

class Baseline:
    target = null

    def __init__(self, target):
        if len(target) != 0:
            self.target = target

    def reduce_mem_usage(self, df):
        start_mem = df.memory_usage().sum() / 1024**2
        print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

        for col in df.columns:
            col_type = df[col].dtype

            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
            else:
                pass

        end_mem = df.memory_usage().sum()
        print('Memory usage of optimization is {:.2f} MB'.format(end_mem))
        print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem)/start_mem))

        return df


    def train_lgb(self
                ,input_x
                ,input_y
                ,input_id
                ,params
                ,list_nfold = [0, 1, 2, 3, 4]
                ,n_splits = 5):
        train_oof = np.zeros(len(input_x))
        metrics = []
        imp = pd.DataFrame()

        # cross-validation
        cv = list(StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=123).
                split(input_x, input_y))

        for nfold in list_nfold:
            print("-"*20, nfold, "-"*20)

            # make dataset
            idx_tr, idx_va = cv[nfold][0], cv[nfold][1]

            x_tr, y_tr, id_tr = input_x.loc[idx_tr, :], input_y[idx_tr], input_id.loc[idx_tr, :]
            x_va, y_va, id_va = input_x.loc[idx_va, :], input_y[idx_va], input_id.loc[idx_va, :]

            print(x_tr.shape, x_va.shape)

            # train
            model = lgb.LGBMClassifier(**params)
            model.fit(x_tr
                ,y_tr
                ,eval_set=[(x_tr, y_tr), (x_va, y_va)]
                ,early_stopping_rounds=100
                ,verbose=100
            )

            fname_lgb = "model_lgb_fold{}.pickle".format(nfold)
            with open(fname_lgb, "wb") as f:
                pickle.dump(model, f, protocol=4)

            # evaluate
            y_tr_pred = model.predict_proba(x_tr)[:,1]
            y_va_pred = model.predict_proba(x_va)[:,1]
            metric_tr = roc_auc_score(y_tr, y_tr_pred)
            metric_va = roc_auc_score(y_va, y_va_pred)
            metrics.append([nfold, metric_tr, metric_va])
            print("[auc] tr:{:4f}, va{:.4f}".format(metric_tr, metric_va))

            # oof
            train_oof[idx_va] = y_va_pred

            # imp
            _imp = pd.DataFrame({"col":input_x.columns, "imp":model.feature_importances_, "nfold":nfold})
            imp = pd.concat([imp, _imp])

        print("-"*20, "result", "-"*20)
        # metrics
        metrics = np.array(metrics)
        print(metrics)
        print("[cv] tr:{:.4f}+-{:.4f}, va:{:.4f}+-{:.4f}".format(
                metrics[:,1].mean(), metrics[:,1].std(),
                metrics[:,2].mean(), metrics[:,2].std(),
        ))
        print("[oof]{:.4f}".format(
                roc_auc_score(input_y, train_oof)
        ))

        # oof
        train_oof = pd.concat([
                input_id,
                pd.DataFrame({"pred": train_oof}),
        ], axis=1)

        # importance
        imp = imp.groupby("col")["imp"].agg(["mean", "std"]).reset_index(drop=False)
        imp.columns = ["col", "imp", "imp_std"]

        return train_oof, imp, metrics


    def predict_lgb(self
                    ,input_x
                    ,input_id
                    ,list_nfold=[0,1,2,3,4]):
        pred = np.zeros((len(input_x), len(list_nfold)))
        for nfold in list_nfold:
            print("-"*20, nfold, "-"*20)
            fname_lgb = "model_lgb_fold{}.pickle".format(nfold)
            with open(fname_lgb, "rb") as f:
                model = pickle.load(f)
            pred[:, nfold] = model.predict_proba(input_x)[:,1]

        pred = pd.concat([
            input_id
            ,pd.DataFrame({"pred": pred.mean(axis=1)})
        ], axis=1)

        print("Done.")

        return pred


    def train_xgb(self
                ,input_x
                ,input_y
                ,input_id
                ,params
                ,list_nfold = [0, 1, 2, 3, 4]
                ,n_splits = 5):
        train_oof = np.zeros(len(input_x))
        metrics = []
        imp = pd.DataFrame()

        # cross-validation
        cv = list(StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=123).
                split(input_x, input_y))

        for nfold in list_nfold:
            print("-"*20, nfold, "-"*20)

            # make dataset
            idx_tr, idx_va = cv[nfold][0], cv[nfold][1]

            x_tr, y_tr, id_tr = input_x.loc[idx_tr, :], input_y[idx_tr], input_id.loc[idx_tr, :]
            x_va, y_va, id_va = input_x.loc[idx_va, :], input_y[idx_va], input_id.loc[idx_va, :]

            print(x_tr.shape, x_va.shape)

            # train
            model = xgb.XGBClassifier(**params)
            model.fit(x_tr
                ,y_tr
                ,eval_set=[(x_tr, y_tr), (x_va, y_va)]
            )

            fname_xgb = "model_xgb_fold{}.pickle".format(nfold)
            with open(fname_xgb, "wb") as f:
                pickle.dump(model, f, protocol=4)

            # evaluate
            y_tr_pred = model.predict_proba(x_tr)[:,1]
            y_va_pred = model.predict_proba(x_va)[:,1]
            metric_tr = roc_auc_score(y_tr, y_tr_pred)
            metric_va = roc_auc_score(y_va, y_va_pred)
            metrics.append([nfold, metric_tr, metric_va])
            print("[auc] tr:{:4f}, va{:.4f}".format(metric_tr, metric_va))

            # oof
            train_oof[idx_va] = y_va_pred

            # imp
            _imp = pd.DataFrame({"col":input_x.columns, "imp":model.feature_importances_, "nfold":nfold})
            imp = pd.concat([imp, _imp])

        print("-"*20, "result", "-"*20)
        # metrics
        metrics = np.array(metrics)
        print(metrics)
        print("[cv] tr:{:.4f}+-{:.4f}, va:{:.4f}+-{:.4f}".format(
                metrics[:,1].mean(), metrics[:,1].std(),
                metrics[:,2].mean(), metrics[:,2].std(),
        ))
        print("[oof]{:.4f}".format(
                roc_auc_score(input_y, train_oof)
        ))

        # oof
        train_oof = pd.concat([
                input_id,
                pd.DataFrame({"pred": train_oof}),
        ], axis=1)

        # importance
        imp = imp.groupby("col")["imp"].agg(["mean", "std"]).reset_index(drop=False)
        imp.columns = ["col", "imp", "imp_std"]

        return train_oof, imp, metrics

    def predict_xgb(self
                    ,input_x
                    ,input_id
                    ,list_nfold=[0,1,2,3,4]):
        pred = np.zeros((len(input_x), len(list_nfold)))
        for nfold in list_nfold:
            print("-"*20, nfold, "-"*20)
            fname_xgb = "model_xgb_fold{}.pickle".format(nfold)
            with open(fname_xgb, "rb") as f:
                model = pickle.load(f)
            pred[:, nfold] = model.predict_proba(input_x)[:,1]

        pred = pd.concat([
            input_id
            ,pd.DataFrame({"pred": pred.mean(axis=1)})
        ], axis=1)

        print("Done.")

        return pred





