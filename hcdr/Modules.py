import numpy as np
import pandas as pd
import math

from sklearn.impute import IterativeImputer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PowerTransformer
from sqlalchemy import null

class Modules:
    target = null

    def __init__(self, target):
        if len(target) != 0:
            self.target = target

    #/*============================================*/#
    # 欠損値を補完
    # column = hc_re_cash_var_pop_amt_down_payment
    #/*============================================*/#
    def process_imputer(self, app_train, app_test, replace_columns, column):
        try:
            imputer = IterativeImputer()
            
            if len(column) != 0:
                replace_columns.append(column)

            app_train_replace = pd.DataFrame(imputer.fit_transform(app_train[replace_columns].copy()), columns=replace_columns)
            app_test_replace = pd.DataFrame(imputer.fit_transform(app_test[replace_columns].copy()), columns=replace_columns)

            # 欠損値を補完した列を再結合
            app_train[replace_columns] = app_train_replace[replace_columns]
            app_test[replace_columns] = app_test_replace[replace_columns]

            # idをint型へ戻す
            #app_train['SK_ID_CURR'] = app_train[["SK_ID_CURR"]].astype(int) 
            #app_test['SK_ID_CURR'] = app_test[["SK_ID_CURR"]].astype(int)
            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    ## Yao-Johnson変換
    # num_cols = ['hc_re_cash_var_pop_amt_down_payment']
    # column = hc_re_cash_var_pop_amt_down_payment
    def process_yj_convert(self, app_train, app_test, column, num_cols):
        try:
            ### 学習データに基づいてYao-Johnson変換を定義
            pt = PowerTransformer(method = 'yeo-johnson')
            pt.fit(app_train[num_cols].copy())

            ### 変換後のデータで各列を置換
            app_train[column] = pt.transform(app_train[num_cols])
            app_test[column] = pt.transform(app_test[num_cols])

            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    ## 標準化
    # num_cols = ['hc_re_cash_variance_samp_sk_dpd']
    def process_standardization(self, app_train, app_test, num_cols):
        try:
            scaler = StandardScaler()
            scaler.fit(app_train[num_cols])
            app_train[num_cols] = scaler.transform(app_train[num_cols])
            app_test[num_cols] = scaler.transform(app_test[num_cols])
            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    # ラベルエンコーディング
    def process_label_encoding(self, app_train, app_test, colmun):
        try:
            app_train[colmun].fillna('BLANK', inplace=True)
            app_test[colmun].fillna('BLANK', inplace=True)
            replace_columns = app_train[colmun].unique().tolist()
            replace_value = [x for x in range(len(replace_columns))]
            app_train[colmun].replace(replace_columns, replace_value, inplace=True)
            app_test[colmun].replace(replace_columns, replace_value, inplace=True)
            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
    
    # one-hot-encoding
    def one_hot_encoding(self, app_train, app_test, cat_col):
        try:
            cat_cols = list()
            cat_cols.append(cat_col)
            ## one-hot encoding
            remove_columns = list(app_train.columns)
            ### 学習データとテストデータを結合しget_dummiesによるone-hot encodingを行う
            all_x = pd.concat([app_train, app_test])
            all_x = pd.get_dummies(all_x, columns=cat_cols)

            ### 置換後の列名を取得
            replased_columns = list(all_x.columns)
            remained_columns = [i for i in replased_columns if i not in remove_columns]

            ### 学習データとテストデータを分割
            app_train = all_x.iloc[:app_train.shape[0], :].reset_index(drop=True)
            app_test  = all_x.iloc[app_train.shape[0]:, :].reset_index(drop=True)
            app_test.drop(['TARGET'], axis=1, inplace=True)
            return app_train,app_test
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise