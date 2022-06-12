from modulefinder import Module
import cupy as cp
import numpy as np
import pandas as pd
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import null, true
import tensorflow as tf

from lightgbm import LGBMClassifier

from sklearn import metrics
from sklearn_pandas import DataFrameMapper
from sklearn.metrics import accuracy_score
from sklearn.metrics import log_loss
from sklearn.metrics import mean_squared_log_error
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.metrics import roc_auc_score
from sklearn.tree import plot_tree
from sklearn.datasets import make_moons

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import SimpleImputer

from keras.layers import Dense, Dropout
from keras.models import Sequential

from six import StringIO

from IPython.display import Image
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import math
from scipy import stats
import numpy as np
import pandas as pd
import tensorflow as tf

from datetime import datetime
from tensorflow import feature_column
#from tensorflow.keras import layers

from tqdm import tqdm

# sklearn preprocessing for dealing with categorical variables
from sklearn.preprocessing import LabelEncoder

# File system manangement
import os

# Suppress warnings 
import warnings
warnings.filterwarnings('ignore')

from Modules import Modules

# python ./rev-cons-
def main():
    print('Starting Process\n')

    modules = Modules('SK_ID_CURR')

    app_train_origin =  pd.read_csv('./home-credit-default-risk/exports/app_train_only_number.csv')
    app_test_origin =  pd.read_csv('./home-credit-default-risk/exports/app_test_only_number.csv')
    app_train_rev_cons = pd.read_csv('./home-credit-default-risk/datasets/app_train_hc_rev-cons_axis-24-monthes.csv')
    app_test_rev_cons = pd.read_csv('./home-credit-default-risk/datasets/app_test_hc_rev-cons_axis-24-monthes.csv')

    # applicationのcolumnを取得する
    app_columns = list(app_test_origin.select_dtypes(include='number').columns)
    app_columns.remove('SK_ID_CURR')

    # applicationのオブジェクトをcopy
    app_train = app_train_origin.copy(app_columns)
    app_test = app_test_origin.copy(app_columns)

    # IDを大文字へキャストする
    app_train_rev_cons = app_train_rev_cons.rename(columns={'sk_id_curr': 'SK_ID_CURR'})
    app_test_rev_cons = app_test_rev_cons.rename(columns={'sk_id_curr': 'SK_ID_CURR'}) 

    # 参照対象の列名をリスト化
    replace_columns = list(app_test_origin.select_dtypes(include='number').columns)
    replace_columns.remove('SK_ID_CURR')

    # 処理対象の列名をリスト化(Rev/Cashのcolumnを取得する)
    processing_columns = list(app_test_rev_cons.select_dtypes(include='number').columns)
    processing_columns.remove('SK_ID_CURR')

    # trainへマージ
    app_train = pd.merge(app_train, app_train_rev_cons, on='SK_ID_CURR', how='left')
    # testへマージ
    app_test = pd.merge(app_test, app_test_rev_cons, on='SK_ID_CURR', how='left')

    # 欠損値を補完する
    #for column in processing_columns:
    #    print("Missing Value Completion Process: " + column + "\n")
    #    result = modules.process_imputer(app_train, app_test, replace_columns, column)
    #    if result != True:
    #        print("Can not Process: " + column + "\n")
    app_train.fillna(0, inplace=True)
    app_test.fillna(0, inplace=True)

    ## Yao-Johnson変換
    for column in processing_columns:
        print('YJ process for ' + column + "\n")
        num_cols = []
        num_cols.append(column)
        result = modules.process_yj_convert(app_train, app_test, column, num_cols)
        if result != True:
            print('!!Can not YJ process : ' + column + " !!\n")
        else:
            print('YJ process Process : ' + column + "\n")

    ## 標準化
    for column in processing_columns:
        print('Standardization Process for ' + column + "\n")
        num_cols = []
        num_cols.append(column)
        result = modules.process_standardization(app_train, app_test, num_cols)
        if result != True:
            print('!!Can not Standardization Process : ' + column + " !!\n")
        else:
            print('Standardization Process : ' + column + "\n")

    # 不要な列を削除
    remove_columns = list(app_test_origin.columns)
    remove_columns.remove('SK_ID_CURR')
    app_train.drop(remove_columns, axis=1, inplace=True)
    app_test.drop(remove_columns, axis=1, inplace=True)

    ### train
    app_train.to_csv(
        path_or_buf="./home-credit-default-risk/exports/hc_only-rev-cons_train_axis-24.csv", # 出力先
        sep=",",                                            # 区切り文字
        index=False,                                        # indexの出力有無
        header=True                                        # headerの出力有無
    )
    ### test
    app_test.to_csv(
        path_or_buf="./home-credit-default-risk/exports/hc_only-rev-cons_test_axis-24.csv", # 出力先
        sep=",",                                            # 区切り文字
        index=False,                                        # indexの出力有無
        header=True                                        # headerの出力有無
    )

    # 処理終了
    print('End Process\n')


if __name__ == "__main__":
    # execute only if run as a script
    main()
