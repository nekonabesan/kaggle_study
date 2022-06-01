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

from Modules import Modules

from tqdm import tqdm

# sklearn preprocessing for dealing with categorical variables
from sklearn.preprocessing import LabelEncoder

# File system manangement
import os

# Suppress warnings 
import warnings
warnings.filterwarnings('ignore')



def main():
    print('Starting Process\n')
    modules = Modules('SK_ID_CURR')
    app_train =  pd.read_csv('./home-credit-default-risk/application_train.csv')
    app_test =  pd.read_csv('./home-credit-default-risk/application_test.csv')

    # applicationの欠損値を補完
    replace_columns = list(app_test.select_dtypes(include='number').columns)
    replace_columns.remove('SK_ID_CURR')

    column = ''
    result = modules.process_imputer(app_train, app_test, replace_columns, column)
    if result != true:
        print("Can not Process: \n")

    ## Yao-Johnson変換
    for column in replace_columns:
        num_cols = []
        num_cols.append(column)
        result = modules.process_yj_convert(app_train, app_test, column, num_cols)
        if result != true:
            print('!!Can not YJ process :' + column + " !!\n")
        else:
            print('YJ process Process :' + column + "\n")

    ## 標準化
    for column in replace_columns:
        num_cols = []
        num_cols.append(column)
        result = modules.process_standardization(app_train, app_test, num_cols)
        if result != true:
            print('!!Can not Standardization Process :' + column + " !!\n")
        else:
            print('Standardization Process :' + column + "\n")
    
    
    ### train
    app_train.to_csv(
        path_or_buf="./home-credit-default-risk/exports/app_train_batch_train.csv", # 出力先
        sep=",",                                            # 区切り文字
        index=False,                                        # indexの出力有無
        header=True                                        # headerの出力有無
    )
    ### test
    app_test.to_csv(
        path_or_buf="./home-credit-default-risk/exports/app_train_batch_test.csv", # 出力先
        sep=",",                                            # 区切り文字
        index=False,                                        # indexの出力有無
        header=True                                        # headerの出力有無
    )
    print('End Process\n')


if __name__ == "__main__":
    # execute only if run as a script
    main()
