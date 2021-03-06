
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
from scipy.stats import ranksums

from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

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

import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

class FeatureEngineering:
    target = null

    def __init__(self, target):
        if len(target) != 0:
            self.target = target


    def reduce_mem_usage(self, data, verbose = True):
        start_mem = data.memory_usage().sum() / 1024**2
        if verbose:
            print('Memory usage of dataframe: {:.2f} MB'.format(start_mem))
        
        for col in data.columns:
            col_type = data[col].dtype
            
            if col_type != object:
                c_min = data[col].min()
                c_max = data[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        data[col] = data[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        data[col] = data[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        data[col] = data[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        data[col] = data[col].astype(np.int64)  
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        data[col] = data[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        data[col] = data[col].astype(np.float32)
                    else:
                        data[col] = data[col].astype(np.float64)

        end_mem = data.memory_usage().sum() / 1024**2
        if verbose:
            print('Memory usage after optimization: {:.2f} MB'.format(end_mem))
            print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
        
        return data


    def one_hot_encoder(self, data, nan_as_category = True):
        original_columns = list(data.columns)
        categorical_columns = [col for col in data.columns \
                            if not pd.api.types.is_numeric_dtype(data[col].dtype)]
        for c in categorical_columns:
            if nan_as_category:
                data[c].fillna('NaN', inplace = True)
            values = list(data[c].unique())
            for v in values:
                data[str(c) + '_' + str(v)] = (data[c] == v).astype(np.uint8)
        data.drop(categorical_columns, axis = 1, inplace = True)
        return data, [c for c in data.columns if c not in original_columns]


    def application_train_test(self, file_path, file_name, nan_as_category = True):
        # Read data and merge
        """
        df_train = pd.read_csv(file_path + 'application_train.csv')
        df_test = pd.read_csv(file_path + 'application_test.csv')
        df = pd.concat([df_train, df_test], axis = 0, ignore_index = True)
        del df_train, df_test
        gc.collect()
        """
        df = pd.read_csv(file_path + file_name)
        # Read data and merge
        df_train = pd.read_csv(file_path + 'application_train.csv')
        df_test = pd.read_csv(file_path + 'application_test.csv')
        df = pd.concat([df_train, df_test], axis = 0, ignore_index = True)
        del df_train, df_test
        gc.collect()
        
        for col in df.columns:
            #if df[col].dtype=='O':
            if (is_string_dtype(df[col])):
                df[col] = df[col].astype(str).str.replace(" ","_")
                df[col] = df[col].astype(str).str.replace(':','_')
                df[col]=  df[col].astype(str).str.replace("/","_")
                df[col] = df[col].astype(str).str.replace(",","")
                df[col] = df[col].astype(str).str.replace(" ","_")
                ###
                df[col] = df[col].astype(str).str.replace('-', '_')
                df[col] = df[col].astype(str).str.replace(r'\,', r'_')
                df[col] = df[col].astype(str).str.replace(r'\(', r'_')
                df[col] = df[col].astype(str).str.replace(r'\)', r'_')
                df[col] = df[col].astype(str).str.replace(r'\+', r'_')

        # Remove some rows with values not present in test set
        df.drop(df[df['CODE_GENDER'] == 'XNA'].index, inplace = True)
        df.drop(df[df['NAME_INCOME_TYPE'] == 'Maternity leave'].index, inplace = True)
        df.drop(df[df['NAME_FAMILY_STATUS'] == 'Unknown'].index, inplace = True)
        #df['CODE_GENDER'].replace(['XNA'], ['M'], inplace=True)
        #df['NAME_INCOME_TYPE'].replace(['Maternityleave'], ['Unemployed'], inplace=True)
        #df['NAME_INCOME_TYPE'].replace(['Maternity_leave'], ['Unemployed'], inplace=True)
        #df['NAME_FAMILY_STATUS'].replace('Unknown', 'Married', inplace=True)
        df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace=True)

        # Remove some empty features
        df.drop(['FLAG_DOCUMENT_2', 'FLAG_DOCUMENT_10', 'FLAG_DOCUMENT_12', 'FLAG_DOCUMENT_13', 'FLAG_DOCUMENT_14', 
                'FLAG_DOCUMENT_15', 'FLAG_DOCUMENT_16', 'FLAG_DOCUMENT_17', 'FLAG_DOCUMENT_19', 'FLAG_DOCUMENT_20', 
                'FLAG_DOCUMENT_21', 
                'EMERGENCYSTATE_MODE', 'FONDKAPREMONT_MODE', 'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE'], axis = 1, inplace = True)

        # ???????????????
        df = df.fillna({'NAME_TYPE_SUITE': 'Unaccompanied'})
        #df = df.fillna(0)
        
        # Replace some outliers
        df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace = True)
        df.loc[df['OWN_CAR_AGE'] > 80, 'OWN_CAR_AGE'] = np.nan
        df.loc[df['REGION_RATING_CLIENT_W_CITY'] < 0, 'REGION_RATING_CLIENT_W_CITY'] = np.nan
        df.loc[df['AMT_INCOME_TOTAL'] > 1e8, 'AMT_INCOME_TOTAL'] = np.nan
        df.loc[df['AMT_REQ_CREDIT_BUREAU_QRT'] > 10, 'AMT_REQ_CREDIT_BUREAU_QRT'] = np.nan
        df.loc[df['OBS_30_CNT_SOCIAL_CIRCLE'] > 40, 'OBS_30_CNT_SOCIAL_CIRCLE'] = np.nan
        
        # Categorical features with Binary encode (0 or 1; two categories)
        for bin_feature in ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']:
            df[bin_feature], _ = pd.factorize(df[bin_feature])
            
        # Categorical features with One-Hot encode
        df, _ = self.one_hot_encoder(df, nan_as_category)
        
        # Some new features
        df['app_missing'] = df.isnull().sum(axis = 1).values
        #ext_source??????
        df['NEW_SOURCES_PROD'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2'] * df['EXT_SOURCE_3']
        #ext_source?????????
        df['app_NEW_EXT_SOURCES_MEAN'] = df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].mean(axis=1)
        #ext_source???????????????
        df['app_NEW_SCORES_STD'] = df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].std(axis=1)

        df['app_EXT_SOURCE_prod'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2'] * df['EXT_SOURCE_3']
        df['app_EXT_SOURCE_1_times_EXT_SOURCE_2'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2']
        df['app_EXT_SOURCE_1_times_EXT_SOURCE_3'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_3']
        df['app_EXT_SOURCE_2_times_EXT_SOURCE_3'] = df['EXT_SOURCE_2'] * df['EXT_SOURCE_3']
        df['app_EXT_SOURCE_1_times_DAYS_EMPLOYED'] = df['EXT_SOURCE_1'] * df['DAYS_EMPLOYED']
        df['app_EXT_SOURCE_2_times_DAYS_EMPLOYED'] = df['EXT_SOURCE_2'] * df['DAYS_EMPLOYED']
        df['app_EXT_SOURCE_3_times_DAYS_EMPLOYED'] = df['EXT_SOURCE_3'] * df['DAYS_EMPLOYED']
        df['app_EXT_SOURCE_1_PER_DAYS_BIRTH'] = df['EXT_SOURCE_1'] / df['DAYS_BIRTH']
        df['app_EXT_SOURCE_2_PER_DAYS_BIRTH'] = df['EXT_SOURCE_2'] / df['DAYS_BIRTH']
        df['app_EXT_SOURCE_3_PER_DAYS_BIRTH'] = df['EXT_SOURCE_3'] / df['DAYS_BIRTH']
        
        df['app_AMT_CREDIT_AMT_GOODS_PRICE'] = df['AMT_CREDIT'] - df['AMT_GOODS_PRICE']
        df['app_AMT_CREDIT_PER_AMT_GOODS_PRICE'] = df['AMT_CREDIT'] / df['AMT_GOODS_PRICE']
        df['app_AMT_CREDIT_PER_AMT_ANNUITY'] = df['AMT_CREDIT'] / df['AMT_ANNUITY']
        #??????
        df['app_PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
        df['app_AMT_CREDIT_PER_AMT_INCOME_TOTAL'] = df['AMT_CREDIT'] / df['AMT_INCOME_TOTAL']
        #?????????????????????????????????????????????
        df['app_INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
        
        df['app_AMT_INCOME_TOTAL_div_12_AMT_ANNUITY'] = df['AMT_INCOME_TOTAL'] / 12. - df['AMT_ANNUITY']
        df['app_AMT_INCOME_TOTAL_PER_AMT_ANNUITY'] = df['AMT_INCOME_TOTAL'] / df['AMT_ANNUITY']
        df['app_ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL'] #????????????????????????????????????
        df['app_AMT_INCOME_TOTAL_AMT_GOODS_PRICE'] = df['AMT_INCOME_TOTAL'] - df['AMT_GOODS_PRICE'] #???????????????1?????????????????????
        df['app_INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
        df['app_AMT_INCOME_TOTAL_div_CNT_CHILDREN'] = df['AMT_INCOME_TOTAL'] / (1 + df['CNT_CHILDREN'])
        
        df['app_most_popular_AMT_GOODS_PRICE'] = df['AMT_GOODS_PRICE'] \
                            .isin([225000, 450000, 675000, 900000]).map({True: 1, False: 0})
        df['app_popular_AMT_GOODS_PRICE'] = df['AMT_GOODS_PRICE'] \
                            .isin([1125000, 1350000, 1575000, 1800000, 2250000]).map({True: 1, False: 0})
        
        df['app_OWN_CAR_AGE_div_DAYS_BIRTH'] = df['OWN_CAR_AGE'] / df['DAYS_BIRTH']
        df['app_OWN_CAR_AGE_div_DAYS_EMPLOYED'] = df['OWN_CAR_AGE'] / df['DAYS_EMPLOYED']
        
        df['app_DAYS_LAST_PHONE_CHANGE_div_DAYS_BIRTH'] = df['DAYS_LAST_PHONE_CHANGE'] / df['DAYS_BIRTH']
        df['app_DAYS_LAST_PHONE_CHANGE_div_DAYS_EMPLOYED'] = df['DAYS_LAST_PHONE_CHANGE'] / df['DAYS_EMPLOYED']
        df['app_DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] - df['DAYS_BIRTH']
        df['app_DAYS_EMPLOYED_div_DAYS_BIRTH'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
        
        df['app_CNT_CHILDREN_div_CNT_FAM_MEMBERS'] = df['CNT_CHILDREN'] / df['CNT_FAM_MEMBERS']

        df = df.replace([np.inf, -np.inf], np.nan)
        
        return self.reduce_mem_usage(df)




    def bureau_and_balance(self, file_path, nan_as_category = True):
        df_bureau_b = self.reduce_mem_usage(pd.read_csv(file_path + 'bureau_balance.csv'), verbose = False)


        for col in df_bureau_b.columns:
            #if df_bureau_b[col].dtype=='O':
            if (is_string_dtype(df_bureau_b[col])):
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(" ","_")
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(':','_')
                df_bureau_b[col]=  df_bureau_b[col].astype(str).str.replace("/","_")
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(",","")
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(" ","_")
                ###
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace('-', '_')
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(r'\,', r'_')
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(r'\(', r'_')
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(r'\)', r'_')
                df_bureau_b[col] = df_bureau_b[col].astype(str).str.replace(r'\+', r'_')

        # ???????????????
        df_bureau_b = df_bureau_b.replace([np.inf, -np.inf], np.nan)
        
        # Some new features in bureau_balance set
        tmp = df_bureau_b[['SK_ID_BUREAU', 'STATUS']].groupby('SK_ID_BUREAU')
        tmp_last = tmp.last()
        tmp_last.columns = ['First_status']
        df_bureau_b = df_bureau_b.join(tmp_last, how = 'left', on = 'SK_ID_BUREAU')
        tmp_first = tmp.first()
        tmp_first.columns = ['Last_status']
        df_bureau_b = df_bureau_b.join(tmp_first, how = 'left', on = 'SK_ID_BUREAU')
        del tmp, tmp_first, tmp_last
        gc.collect()
        
        tmp = df_bureau_b[['SK_ID_BUREAU', 'MONTHS_BALANCE']].groupby('SK_ID_BUREAU').last()
        tmp = tmp.apply(abs)
        tmp.columns = ['Month']
        df_bureau_b = df_bureau_b.join(tmp, how = 'left', on = 'SK_ID_BUREAU')
        del tmp
        gc.collect()
        
        tmp = df_bureau_b.loc[df_bureau_b['STATUS'] == 'C', ['SK_ID_BUREAU', 'MONTHS_BALANCE']] \
                    .groupby('SK_ID_BUREAU').last()
        tmp = tmp.apply(abs)
        tmp.columns = ['When_closed']
        df_bureau_b = df_bureau_b.join(tmp, how = 'left', on = 'SK_ID_BUREAU')
        del tmp
        gc.collect()
        
        df_bureau_b['Month_closed_to_end'] = df_bureau_b['Month'] - df_bureau_b['When_closed']

        for c in range(6):
            tmp = df_bureau_b.loc[df_bureau_b['STATUS'] == str(c), ['SK_ID_BUREAU', 'MONTHS_BALANCE']] \
                            .groupby('SK_ID_BUREAU').count()
            tmp.columns = ['DPD_' + str(c) + '_cnt']
            df_bureau_b = df_bureau_b.join(tmp, how = 'left', on = 'SK_ID_BUREAU')
            df_bureau_b['DPD_' + str(c) + '_Month'] = df_bureau_b['DPD_' + str(c) + '_cnt'] / df_bureau_b['Month']
            del tmp
            gc.collect()
        df_bureau_b['Non_zero_DPD_cnt'] = df_bureau_b[['DPD_1_cnt', 'DPD_2_cnt', 'DPD_3_cnt', 'DPD_4_cnt', 'DPD_5_cnt']].sum(axis = 1)
        
        df_bureau_b, bureau_b_cat = self.one_hot_encoder(df_bureau_b, nan_as_category)

        # Bureau balance: Perform aggregations 
        aggregations = {}
        for col in df_bureau_b.columns:
            aggregations[col] = ['mean'] if col in bureau_b_cat else ['min', 'max', 'size']
        df_bureau_b_agg = df_bureau_b.groupby('SK_ID_BUREAU').agg(aggregations)
        df_bureau_b_agg.columns = pd.Index([e[0] + "_" + e[1].upper() for e in df_bureau_b_agg.columns.tolist()])
        del df_bureau_b
        gc.collect()

        df_bureau = self.reduce_mem_usage(pd.read_csv(file_path + 'bureau.csv'), verbose = False)

        for col in df_bureau.columns:
            #if df_bureau[col].dtype=='O':
            if (is_string_dtype(df_bureau[col])):
                df_bureau[col] = df_bureau[col].astype(str).str.replace(" ","_")
                df_bureau[col] = df_bureau[col].astype(str).str.replace(':','_')
                df_bureau[col]=  df_bureau[col].astype(str).str.replace("/","_")
                df_bureau[col] = df_bureau[col].astype(str).str.replace(",","")
                df_bureau[col] = df_bureau[col].astype(str).str.replace(" ","_")
                ###
                df_bureau[col] = df_bureau[col].astype(str).str.replace('-', '_')
                df_bureau[col] = df_bureau[col].astype(str).str.replace(r'\,', r'_')
                df_bureau[col] = df_bureau[col].astype(str).str.replace(r'\(', r'_')
                df_bureau[col] = df_bureau[col].astype(str).str.replace(r'\)', r'_')
                df_bureau[col] = df_bureau[col].astype(str).str.replace(r'\+', r'_')
        
        # ???????????????
        df_bureau = df_bureau.replace([np.inf, -np.inf], np.nan)
        #df_bureau = df_bureau.fillna(0)
                    
        # Replace\remove some outliers in bureau set
        df_bureau.loc[df_bureau['AMT_ANNUITY'] > .8e8, 'AMT_ANNUITY'] = np.nan
        df_bureau.loc[df_bureau['AMT_CREDIT_SUM'] > 3e8, 'AMT_CREDIT_SUM'] = np.nan
        df_bureau.loc[df_bureau['AMT_CREDIT_SUM_DEBT'] > 1e8, 'AMT_CREDIT_SUM_DEBT'] = np.nan
        df_bureau.loc[df_bureau['AMT_CREDIT_MAX_OVERDUE'] > .8e8, 'AMT_CREDIT_MAX_OVERDUE'] = np.nan
        df_bureau.loc[df_bureau['DAYS_ENDDATE_FACT'] < -10000, 'DAYS_ENDDATE_FACT'] = np.nan
        df_bureau.loc[(df_bureau['DAYS_CREDIT_UPDATE'] > 0) | (df_bureau['DAYS_CREDIT_UPDATE'] < -40000), 'DAYS_CREDIT_UPDATE'] = np.nan
        df_bureau.loc[df_bureau['DAYS_CREDIT_ENDDATE'] < -10000, 'DAYS_CREDIT_ENDDATE'] = np.nan
        
        df_bureau.drop(df_bureau[df_bureau['DAYS_ENDDATE_FACT'] < df_bureau['DAYS_CREDIT']].index, inplace = True)
        
        # Some new features in bureau set
        df_bureau['bureau_AMT_CREDIT_SUM__AMT_CREDIT_SUM_DEBT'] = df_bureau['AMT_CREDIT_SUM'] - df_bureau['AMT_CREDIT_SUM_DEBT']
        df_bureau['bureau_AMT_CREDIT_SUM__AMT_CREDIT_SUM_LIMIT'] = df_bureau['AMT_CREDIT_SUM'] - df_bureau['AMT_CREDIT_SUM_LIMIT']
        df_bureau['bureau_AMT_CREDIT_SUM__AMT_CREDIT_SUM_OVERDUE'] = df_bureau['AMT_CREDIT_SUM'] - df_bureau['AMT_CREDIT_SUM_OVERDUE']

        df_bureau['bureau_DAYS_CREDIT__CREDIT_DAY_OVERDUE'] = df_bureau['DAYS_CREDIT'] - df_bureau['CREDIT_DAY_OVERDUE']
        df_bureau['bureau_DAYS_CREDIT__DAYS_CREDIT_ENDDATE'] = df_bureau['DAYS_CREDIT'] - df_bureau['DAYS_CREDIT_ENDDATE']
        df_bureau['bureau_DAYS_CREDIT__DAYS_ENDDATE_FACT'] = df_bureau['DAYS_CREDIT'] - df_bureau['DAYS_ENDDATE_FACT']
        df_bureau['bureau_DAYS_CREDIT_ENDDATE__DAYS_ENDDATE_FACT'] = df_bureau['DAYS_CREDIT_ENDDATE'] - df_bureau['DAYS_ENDDATE_FACT']
        df_bureau['bureau_DAYS_CREDIT_UPDATE__DAYS_CREDIT_ENDDATE'] = df_bureau['DAYS_CREDIT_UPDATE'] - df_bureau['DAYS_CREDIT_ENDDATE']
        
        # Categorical features with One-Hot encode
        df_bureau, bureau_cat = self.one_hot_encoder(df_bureau, nan_as_category)
        
        # Bureau balance: merge with bureau.csv
        df_bureau = df_bureau.join(df_bureau_b_agg, how = 'left', on = 'SK_ID_BUREAU')
        df_bureau.drop('SK_ID_BUREAU', axis = 1, inplace = True)
        del df_bureau_b_agg
        gc.collect()
        
        # Bureau and bureau_balance aggregations for application set
        categorical = bureau_cat + bureau_b_cat
        aggregations = {}
        for col in df_bureau.columns:
            aggregations[col] = ['mean'] if col in categorical else ['min', 'max', 'size', 'mean', 'var', 'sum']
        df_bureau_agg = df_bureau.groupby('SK_ID_CURR').agg(aggregations)
        df_bureau_agg.columns = pd.Index(['BURO_' + e[0] + "_" + e[1].upper() for e in df_bureau_agg.columns.tolist()])
        
        # Bureau: Active credits
        active_agg = df_bureau[df_bureau['CREDIT_ACTIVE_Active'] == 1].groupby('SK_ID_CURR').agg(aggregations)
        active_agg.columns = pd.Index(['ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
        df_bureau_agg = df_bureau_agg.join(active_agg, how = 'left')
        del active_agg
        gc.collect()
        
        # Bureau: Closed credits
        closed_agg = df_bureau[df_bureau['CREDIT_ACTIVE_Closed'] == 1].groupby('SK_ID_CURR').agg(aggregations)
        closed_agg.columns = pd.Index(['CLOSED_' + e[0] + "_" + e[1].upper() for e in closed_agg.columns.tolist()])
        df_bureau_agg = df_bureau_agg.join(closed_agg, how = 'left')
        del closed_agg, df_bureau
        gc.collect()

        df_bureau_agg = df_bureau_agg.replace([np.inf, -np.inf], np.nan)
        df_bureau_agg = df_bureau_agg.fillna(df_bureau_agg.max() + (df_bureau_agg.max() * 0.4))

        return self.reduce_mem_usage(df_bureau_agg)




    def previous_application(self, file_path, nan_as_category = True):
        df_prev = pd.read_csv(file_path + 'previous_application.csv')

        for col in df_prev.columns:
            if df_prev[col].dtype=='O':
                df_prev[col] = df_prev[col].astype(str).str.replace(" ","_")
                df_prev[col] = df_prev[col].astype(str).str.replace(':','_')
                df_prev[col]=  df_prev[col].astype(str).str.replace("/","_")
                df_prev[col] = df_prev[col].astype(str).str.replace(",","")
                df_prev[col] = df_prev[col].astype(str).str.replace(" ","_")
                ###
                df_prev[col] = df_prev[col].astype(str).str.replace('-', '_')
                df_prev[col] = df_prev[col].astype(str).str.replace(r'\,', r'_')
                df_prev[col] = df_prev[col].astype(str).str.replace(r'\(', r'_')
                df_prev[col] = df_prev[col].astype(str).str.replace(r'\)', r'_')
                df_prev[col] = df_prev[col].astype(str).str.replace(r'\+', r'_')

        # ???????????????
        #df_prev = df_prev.fillna(0)

        #df_prev['CHANNEL_TYPE'] = df_prev['CHANNEL_TYPE'].replace("AP+_(Cash_loan)", "AP_Cash_loan")
        # Replace some outliers
        df_prev.loc[df_prev['AMT_CREDIT'] > 6000000, 'AMT_CREDIT'] = np.nan
        df_prev.loc[df_prev['SELLERPLACE_AREA'] > 3500000, 'SELLERPLACE_AREA'] = np.nan
        df_prev[['DAYS_FIRST_DRAWING', 'DAYS_FIRST_DUE', 'DAYS_LAST_DUE_1ST_VERSION', 
                'DAYS_LAST_DUE', 'DAYS_TERMINATION']].replace(365243, np.nan, inplace = True)
        
        # Some new features
        df_prev['prev_missing'] = df_prev.isnull().sum(axis = 1).values
        df_prev['prev_AMT_APPLICATION_div_AMT_CREDIT'] = df_prev['AMT_APPLICATION'] / df_prev['AMT_CREDIT']
        df_prev['prev_AMT_APPLICATION__AMT_CREDIT'] = df_prev['AMT_APPLICATION'] - df_prev['AMT_CREDIT']
        df_prev['prev_AMT_APPLICATION__AMT_GOODS_PRICE'] = df_prev['AMT_APPLICATION'] - df_prev['AMT_GOODS_PRICE']
        df_prev['prev_AMT_GOODS_PRICE__AMT_CREDIT'] = df_prev['AMT_GOODS_PRICE'] - df_prev['AMT_CREDIT']
        df_prev['prev_DAYS_FIRST_DRAWING__DAYS_FIRST_DUE'] = df_prev['DAYS_FIRST_DRAWING'] - df_prev['DAYS_FIRST_DUE']
        df_prev['prev_DAYS_TERMINATION_less__500'] = (df_prev['DAYS_TERMINATION'] < -500).astype(int)
        
        # Categorical features with One-Hot encode
        df_prev, categorical = self.one_hot_encoder(df_prev, nan_as_category)

        # Aggregations for application set
        aggregations = {}
        for col in df_prev.columns:
            aggregations[col] = ['mean'] if col in categorical else ['min', 'max', 'size', 'mean', 'var', 'sum']
        df_prev_agg = df_prev.groupby('SK_ID_CURR').agg(aggregations)
        df_prev_agg.columns = pd.Index(['PREV_' + e[0] + "_" + e[1].upper() for e in df_prev_agg.columns.tolist()])
        
        # Previous Applications: Approved Applications
        approved_agg = df_prev[df_prev['NAME_CONTRACT_STATUS_Approved'] == 1].groupby('SK_ID_CURR').agg(aggregations)
        approved_agg.columns = pd.Index(['APPROVED_' + e[0] + '_' + e[1].upper() for e in approved_agg.columns.tolist()])
        df_prev_agg = df_prev_agg.join(approved_agg, how = 'left')
        del approved_agg
        gc.collect()
        
        # Previous Applications: Refused Applications
        refused_agg = df_prev[df_prev['NAME_CONTRACT_STATUS_Refused'] == 1].groupby('SK_ID_CURR').agg(aggregations)
        refused_agg.columns = pd.Index(['REFUSED_' + e[0] + "_" + e[1].upper() for e in refused_agg.columns.tolist()])
        df_prev_agg = df_prev_agg.join(refused_agg, how = 'left')
        del refused_agg, df_prev
        gc.collect()

        df_prev_agg = df_prev_agg.replace([np.inf, -np.inf], np.nan)
        df_prev_agg = df_prev_agg.fillna(df_prev_agg.max() + (df_prev_agg.max() * 0.4))
        
        return self.reduce_mem_usage(df_prev_agg)



    def pos_cash(self, file_path, nan_as_category = True):
        df_pos = pd.read_csv(file_path + 'POS_CASH_balance.csv')

        for col in df_pos.columns:
            if df_pos[col].dtype=='O':
                df_pos[col] = df_pos[col].astype(str).str.replace(" ","_")
                df_pos[col] = df_pos[col].astype(str).str.replace(':','_')
                df_pos[col]=  df_pos[col].astype(str).str.replace("/","_")
                df_pos[col] = df_pos[col].astype(str).str.replace(",","")
                df_pos[col] = df_pos[col].astype(str).str.replace(" ","_")
                ###
                df_pos[col] = df_pos[col].astype(str).str.replace('-', '_')
                df_pos[col] = df_pos[col].astype(str).str.replace(r'\,', r'_')
                df_pos[col] = df_pos[col].astype(str).str.replace(r'\(', r'_')
                df_pos[col] = df_pos[col].astype(str).str.replace(r'\)', r'_')
                df_pos[col] = df_pos[col].astype(str).str.replace(r'\+', r'_')

        # ????????????
        #df_pos = df_pos.fillna(0)
        
        
        # Replace some outliers
        df_pos.loc[df_pos['CNT_INSTALMENT_FUTURE'] > 60, 'CNT_INSTALMENT_FUTURE'] = np.nan
        
        # Some new features
        df_pos['pos_CNT_INSTALMENT_more_CNT_INSTALMENT_FUTURE'] = \
                        (df_pos['CNT_INSTALMENT'] > df_pos['CNT_INSTALMENT_FUTURE']).astype(int)
        
        # Categorical features with One-Hot encode
        df_pos, categorical = self.one_hot_encoder(df_pos, nan_as_category)
        
        # Aggregations for application set
        aggregations = {}
        for col in df_pos.columns:
            aggregations[col] = ['mean'] if col in categorical else ['min', 'max', 'size', 'mean', 'var', 'sum']
        df_pos_agg = df_pos.groupby('SK_ID_CURR').agg(aggregations)
        df_pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in df_pos_agg.columns.tolist()])

        # Count POS lines
        df_pos_agg['POS_COUNT'] = df_pos.groupby('SK_ID_CURR').size()
        del df_pos
        gc.collect()

        df_pos_agg = df_pos_agg.replace([np.inf, -np.inf], np.nan)
        df_pos_agg = df_pos_agg.fillna(df_pos_agg.max() + (df_pos_agg.max() * 0.4))
        
        return self.reduce_mem_usage(df_pos_agg)


    def installments_payments(self, file_path, nan_as_category = True):
        df_ins = pd.read_csv(file_path + 'installments_payments.csv')

        for col in df_ins.columns:
            if df_ins[col].dtype=='O':
                df_ins[col] = df_ins[col].astype(str).str.replace(" ","_")
                df_ins[col] = df_ins[col].astype(str).str.replace(':','_')
                df_ins[col]=  df_ins[col].astype(str).str.replace("/","_")
                df_ins[col] = df_ins[col].astype(str).str.replace(",","")
                df_ins[col] = df_ins[col].astype(str).str.replace(" ","_")
                ###
                df_ins[col] = df_ins[col].astype(str).str.replace('-', '_')
                df_ins[col] = df_ins[col].astype(str).str.replace(r'\,', r'_')
                df_ins[col] = df_ins[col].astype(str).str.replace(r'\(', r'_')
                df_ins[col] = df_ins[col].astype(str).str.replace(r'\)', r'_')
                df_ins[col] = df_ins[col].astype(str).str.replace(r'\+', r'_')

        # ???????????????
        #df_ins = df_ins.fillna(0)
        
        # Replace some outliers
        df_ins.loc[df_ins['NUM_INSTALMENT_VERSION'] > 70, 'NUM_INSTALMENT_VERSION'] = np.nan
        df_ins.loc[df_ins['DAYS_ENTRY_PAYMENT'] < -4000, 'DAYS_ENTRY_PAYMENT'] = np.nan
        
        # Some new features
        df_ins['ins_DAYS_ENTRY_PAYMENT_DAYS_INSTALMENT'] = df_ins['DAYS_ENTRY_PAYMENT'] - df_ins['DAYS_INSTALMENT']
        df_ins['ins_NUM_INSTALMENT_NUMBER_100'] = (df_ins['NUM_INSTALMENT_NUMBER'] == 100).astype(int)
        df_ins['ins_DAYS_INSTALMENT_more_NUM_INSTALMENT_NUMBER'] = (df_ins['DAYS_INSTALMENT'] > df_ins['NUM_INSTALMENT_NUMBER'] * 50 / 3 - 11500 / 3).astype(int)
        df_ins['ins_AMT_INSTALMENT_AMT_PAYMENT'] = df_ins['AMT_INSTALMENT'] - df_ins['AMT_PAYMENT']
        df_ins['ins_AMT_PAYMENT_div_AMT_INSTALMENT'] = df_ins['AMT_PAYMENT'] / df_ins['AMT_INSTALMENT']
        
        # Categorical features with One-Hot encode
        df_ins, categorical = self.one_hot_encoder(df_ins, nan_as_category)

        # Aggregations for application set
        aggregations = {}
        for col in df_ins.columns:
            aggregations[col] = ['mean'] if col in categorical else ['min', 'max', 'size', 'mean', 'var', 'sum']
        df_ins_agg = df_ins.groupby('SK_ID_CURR').agg(aggregations)
        df_ins_agg.columns = pd.Index(['INS_' + e[0] + "_" + e[1].upper() for e in df_ins_agg.columns.tolist()])
        
        # Count installments lines
        df_ins_agg['INSTAL_COUNT'] = df_ins.groupby('SK_ID_CURR').size()
        del df_ins
        gc.collect()

        df_ins_agg = df_ins_agg.replace([np.inf, -np.inf], np.nan)
        df_ins_agg = df_ins_agg.fillna(df_ins_agg.max() + (df_ins_agg.max() * 0.4))
        
        return self.reduce_mem_usage(df_ins_agg)




    def credit_card_balance(self, file_path, nan_as_category = True):
        df_card = pd.read_csv(file_path + 'credit_card_balance.csv')

        for col in df_card.columns:
            if df_card[col].dtype=='O':
                df_card[col] = df_card[col].astype(str).str.replace(" ","_")
                df_card[col] = df_card[col].astype(str).str.replace(':','_')
                df_card[col]=  df_card[col].astype(str).str.replace("/","_")
                df_card[col] = df_card[col].astype(str).str.replace(",","")
                df_card[col] = df_card[col].astype(str).str.replace(" ","_")
                ###
                df_card[col] = df_card[col].astype(str).str.replace('-', '_')
                df_card[col] = df_card[col].astype(str).str.replace(r'\,', r'_')
                df_card[col] = df_card[col].astype(str).str.replace(r'\(', r'_')
                df_card[col] = df_card[col].astype(str).str.replace(r'\)', r'_')
                df_card[col] = df_card[col].astype(str).str.replace(r'\+', r'_')

        # ???????????????
        #df_card = df_card.fillna(0)
        
        # Replace some outliers
        df_card.loc[df_card['AMT_PAYMENT_CURRENT'] > 4000000, 'AMT_PAYMENT_CURRENT'] = np.nan
        df_card.loc[df_card['AMT_CREDIT_LIMIT_ACTUAL'] > 1000000, 'AMT_CREDIT_LIMIT_ACTUAL'] = np.nan

        # Some new features
        df_card['card_missing'] = df_card.isnull().sum(axis = 1).values
        df_card['card_SK_DPD__MONTHS_BALANCE'] = df_card['SK_DPD'] - df_card['MONTHS_BALANCE']
        df_card['card_SK_DPD_DEF__MONTHS_BALANCE'] = df_card['SK_DPD_DEF'] - df_card['MONTHS_BALANCE']
        df_card['card_SK_DPD__SK_DPD_DEF'] = df_card['SK_DPD'] - df_card['SK_DPD_DEF']
        
        df_card['card_AMT_TOTAL_RECEIVABLE__AMT_RECIVABLE'] = df_card['AMT_TOTAL_RECEIVABLE'] - df_card['AMT_RECIVABLE']
        df_card['card_AMT_TOTAL_RECEIVABLE__AMT_RECEIVABLE_PRINCIPAL'] = df_card['AMT_TOTAL_RECEIVABLE'] - df_card['AMT_RECEIVABLE_PRINCIPAL']
        df_card['card_AMT_RECIVABLE__AMT_RECEIVABLE_PRINCIPAL'] = df_card['AMT_RECIVABLE'] - df_card['AMT_RECEIVABLE_PRINCIPAL']

        df_card['card_AMT_BALANCE__AMT_RECIVABLE'] = df_card['AMT_BALANCE'] - df_card['AMT_RECIVABLE']
        df_card['card_AMT_BALANCE__AMT_RECEIVABLE_PRINCIPAL'] = df_card['AMT_BALANCE'] - df_card['AMT_RECEIVABLE_PRINCIPAL']
        df_card['card_AMT_BALANCE__AMT_TOTAL_RECEIVABLE'] = df_card['AMT_BALANCE'] - df_card['AMT_TOTAL_RECEIVABLE']

        df_card['card_AMT_DRAWINGS_CURRENT__AMT_DRAWINGS_ATM_CURRENT'] = df_card['AMT_DRAWINGS_CURRENT'] - df_card['AMT_DRAWINGS_ATM_CURRENT']
        df_card['card_AMT_DRAWINGS_CURRENT__AMT_DRAWINGS_OTHER_CURRENT'] = df_card['AMT_DRAWINGS_CURRENT'] - df_card['AMT_DRAWINGS_OTHER_CURRENT']
        df_card['card_AMT_DRAWINGS_CURRENT__AMT_DRAWINGS_POS_CURRENT'] = df_card['AMT_DRAWINGS_CURRENT'] - df_card['AMT_DRAWINGS_POS_CURRENT']
        
        # Categorical features with One-Hot encode
        df_card, categorical = self.one_hot_encoder(df_card, nan_as_category)
        
        # Aggregations for application set
        aggregations = {}
        for col in df_card.columns:
            aggregations[col] = ['mean'] if col in categorical else ['min', 'max', 'size', 'mean', 'var', 'sum']
        df_card_agg = df_card.groupby('SK_ID_CURR').agg(aggregations)
        df_card_agg.columns = pd.Index(['CARD_' + e[0] + "_" + e[1].upper() for e in df_card_agg.columns.tolist()])

        # Count credit card lines
        df_card_agg['CARD_COUNT'] = df_card.groupby('SK_ID_CURR').size()
        del df_card
        gc.collect()

        df_card_agg = df_card_agg.replace([np.inf, -np.inf], np.nan)
        df_card_agg = df_card_agg.fillna(df_card_agg.max() + (df_card_agg.max() * 0.4))
        
        return self.reduce_mem_usage(df_card_agg)




    def aggregate(self, file_path):
        warnings.simplefilter(action = 'ignore')
        
        print('-' * 20)
        print('1: application train & test (', time.ctime(), ')')
        print('-' * 20)
        df = self.application_train_test(file_path)
        print('     DF shape:', df.shape)
        
        print('-' * 20)
        print('2: bureau & balance (', time.ctime(), ')')
        print('-' * 20)
        bureau = self.bureau_and_balance(file_path)
        df = df.join(bureau, how = 'left', on = 'SK_ID_CURR')
        print('     DF shape:', df.shape)
        del bureau
        gc.collect()
        
        print('-' * 20)
        print('3: previous_application (', time.ctime(), ')')
        print('-' * 20)
        prev = self.previous_application(file_path)
        df = df.join(prev, how = 'left', on = 'SK_ID_CURR')
        print('     DF shape:', df.shape)
        del prev
        gc.collect()
        
        print('-' * 20)
        print('4: POS_CASH_balance (', time.ctime(), ')')
        print('-' * 20)
        pos = self.pos_cash(file_path)
        df = df.join(pos, how = 'left', on = 'SK_ID_CURR')
        print('     DF shape:', df.shape)
        del pos
        gc.collect()
        
        print('-' * 20)
        print('5: installments_payments (', time.ctime(), ')')
        print('-' * 20)
        ins = self.installments_payments(file_path)
        df = df.join(ins, how = 'left', on = 'SK_ID_CURR')
        print('     DF shape:', df.shape)
        del ins
        gc.collect()
        
        print('-' * 20)
        print('6: credit_card_balance (', time.ctime(), ')')
        print('-' * 20)
        cc = self.credit_card_balance(file_path)
        df = df.join(cc, how = 'left', on = 'SK_ID_CURR')
        print('     DF shape:', df.shape)
        del cc
        gc.collect()
        
        print('-' * 20)
        print('7: final dataset (', time.ctime(), ')')
        print('-' * 20)
        return self.reduce_mem_usage(df)




    def corr_feature_with_target(self, feature, target):
        c0 = feature[target == 0].dropna()
        c1 = feature[target == 1].dropna()
            
        if set(feature.unique()) == set([0, 1]):
            diff = abs(c0.mean(axis = 0) - c1.mean(axis = 0))
        else:
            diff = abs(c0.median(axis = 0) - c1.median(axis = 0))
            
        p = ranksums(c0, c1)[1] if ((len(c0) >= 20) & (len(c1) >= 20)) else 2
            
        return [diff, p]


    


    def clean_data(self, data):
        warnings.simplefilter(action = 'ignore')
        
        # Removing empty features
        nun = data.nunique()
        empty = list(nun[nun <= 1].index)
        
        data.drop(empty, axis = 1, inplace = True)
        print('After removing empty features there are {0:d} features'.format(data.shape[1]))
        
        # Removing features with the same distribution on 0 and 1 classes
        corr = pd.DataFrame(index = ['diff', 'p'])
        ind = data[data['TARGET'].notnull()].index
        
        for c in data.columns.drop('TARGET'):
            corr[c] = self.corr_feature_with_target(data.loc[ind, c], data.loc[ind, 'TARGET'])

        corr = corr.T
        corr['diff_norm'] = abs(corr['diff'] / data.mean(axis = 0))
        
        to_del_1 = corr[((corr['diff'] == 0) & (corr['p'] > .05))].index
        to_del_2 = corr[((corr['diff_norm'] < .5) & (corr['p'] > .05))].drop(to_del_1).index
        to_del = list(to_del_1) + list(to_del_2)
        if 'SK_ID_CURR' in to_del:
            to_del.remove('SK_ID_CURR')
            
        data.drop(to_del, axis = 1, inplace = True)
        print('After removing features with the same distribution on 0 and 1 classes there are {0:d} features'.format(data.shape[1]))
        
        # Removing features with not the same distribution on train and test datasets
        corr_test = pd.DataFrame(index = ['diff', 'p'])
        target = data['TARGET'].notnull().astype(int)
        
        for c in data.columns.drop('TARGET'):
            corr_test[c] = self.corr_feature_with_target(data[c], target)

        corr_test = corr_test.T
        corr_test['diff_norm'] = abs(corr_test['diff'] / data.mean(axis = 0))
        
        bad_features = corr_test[((corr_test['p'] < .05) & (corr_test['diff_norm'] > 1))].index
        bad_features = corr.loc[bad_features][corr['diff_norm'] == 0].index
        
        data.drop(bad_features, axis = 1, inplace = True)
        print('After removing features with not the same distribution on train and test datasets there are {0:d} features'.format(data.shape[1]))
        
        del corr, corr_test
        gc.collect()
        
        # Removing features not interesting for classifier
        clf = LGBMClassifier(random_state = 0)
        train_index = data[data['TARGET'].notnull()].index
        train_columns = data.drop('TARGET', axis = 1).columns

        score = 1
        new_columns = []
        while score > .7:
            train_columns = train_columns.drop(new_columns)
            clf.fit(data.loc[train_index, train_columns], data.loc[train_index, 'TARGET'])
            f_imp = pd.Series(clf.feature_importances_, index = train_columns)
            score = roc_auc_score(data.loc[train_index, 'TARGET'], 
                                clf.predict_proba(data.loc[train_index, train_columns])[:, 1])
            new_columns = f_imp[f_imp > 0].index

        data.drop(train_columns, axis = 1, inplace = True)
        print('After removing features not interesting for classifier there are {0:d} features'.format(data.shape[1]))

        return data

    


    