# load libraries
import gc
import re
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold
import warnings

warnings.filterwarnings('ignore')

class FeatureEngineering2:
    target = 'SK_ID_CURR'
    nan_as_category = True

    def __init__(self, target):
        if len(target) != 0:
            self.target = target

    # run functions and pre_settings
    def one_hot_encoder(self, df, nan_as_category=True):
        original_columns = list(df.columns)
        categorical_columns = [col for col in df.columns if df[col].dtype == 'object']
        df = pd.get_dummies(df, columns=categorical_columns, dummy_na=nan_as_category)
        new_columns = [c for c in df.columns if c not in original_columns]
        return df, new_columns

    def group(self, df_to_agg, prefix, aggregations, aggregate_by= 'SK_ID_CURR'):
        agg_df = df_to_agg.groupby(aggregate_by).agg(aggregations)
        agg_df.columns = pd.Index(['{}{}_{}'.format(prefix, e[0], e[1].upper())
                                for e in agg_df.columns.tolist()])
        return agg_df.reset_index()

    def group_and_merge(self, df_to_agg, df_to_merge, prefix, aggregations, aggregate_by= 'SK_ID_CURR'):
        agg_df = self.group(df_to_agg, prefix, aggregations, aggregate_by= aggregate_by)
        return df_to_merge.merge(agg_df, how='left', on= aggregate_by)

    def do_sum(self, dataframe, group_cols, counted, agg_name):
        gp = dataframe[group_cols + [counted]].groupby(group_cols)[counted].sum().reset_index().rename(columns={counted: agg_name})
        dataframe = dataframe.merge(gp, on=group_cols, how='left')
        return dataframe

    def reduce_mem_usage(self, dataframe):
        m_start = dataframe.memory_usage().sum() / 1024 ** 2
        for col in dataframe.columns:
            col_type = dataframe[col].dtype
            if col_type != object:
                c_min = dataframe[col].min()
                c_max = dataframe[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        dataframe[col] = dataframe[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        dataframe[col] = dataframe[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        dataframe[col] = dataframe[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        dataframe[col] = dataframe[col].astype(np.int64)
                elif str(col_type)[:5] == 'float':
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        dataframe[col] = dataframe[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        dataframe[col] = dataframe[col].astype(np.float32)
                    else:
                        dataframe[col] = dataframe[col].astype(np.float64)

        m_end = dataframe.memory_usage().sum() / 1024 ** 2
        return dataframe


    def risk_groupanizer(self, dataframe, column_names, target_val=1, upper_limit_ratio=8.2, lower_limit_ratio=8.2):
        # one-hot encoder killer :-)
        all_cols = dataframe.columns
        for col in column_names:

            temp_df = dataframe.groupby([col] + ['TARGET'])[['SK_ID_CURR']].count().reset_index()
            temp_df['ratio%'] = round(temp_df['SK_ID_CURR']*100/temp_df.groupby([col])['SK_ID_CURR'].transform('sum'), 1)
            col_groups_high_risk = temp_df[(temp_df['TARGET'] == target_val) &
                                        (temp_df['ratio%'] >= upper_limit_ratio)][col].tolist()
            col_groups_low_risk = temp_df[(temp_df['TARGET'] == target_val) &
                                        (lower_limit_ratio >= temp_df['ratio%'])][col].tolist()
            if upper_limit_ratio != lower_limit_ratio:
                col_groups_medium_risk = temp_df[(temp_df['TARGET'] == target_val) &
                    (upper_limit_ratio > temp_df['ratio%']) & (temp_df['ratio%'] > lower_limit_ratio)][col].tolist()

                for risk, col_groups in zip(['_high_risk', '_medium_risk', '_low_risk'],
                                            [col_groups_high_risk, col_groups_medium_risk, col_groups_low_risk]):
                    dataframe[col + risk] = [1 if val in col_groups else 0 for val in dataframe[col].values]
            else:
                for risk, col_groups in zip(['_high_risk', '_low_risk'], [col_groups_high_risk, col_groups_low_risk]):
                    dataframe[col + risk] = [1 if val in col_groups else 0 for val in dataframe[col].values]
            if dataframe[col].dtype == 'O' or dataframe[col].dtype == 'object':
                dataframe.drop(col, axis=1, inplace=True)
        return dataframe, list(set(dataframe.columns).difference(set(all_cols)))


    def ligthgbm_feature_selection(self, dataframe, index_cols, auc_limit):

        dataframe = dataframe.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))
        clf = LGBMClassifier(random_state=0)
        train_df = dataframe[dataframe['TARGET'].notnull()]
        train_df_X = train_df.drop('TARGET', axis=1)
        train_df_y = train_df['TARGET']
        train_columns = [col for col in train_df_X.columns if col not in index_cols]

        max_auc_score = 1
        best_cols = []
        while max_auc_score > auc_limit:
            train_columns = [col for col in train_columns if col not in best_cols]
            clf.fit(train_df_X[train_columns], train_df_y)
            feats_imp = pd.Series(clf.feature_importances_, index=train_columns)
            max_auc_score = roc_auc_score(train_df_y, clf.predict_proba(train_df_X[train_columns])[:, 1])
            best_cols = feats_imp[feats_imp > 0].index.tolist()

        dataframe.drop(train_columns, axis=1, inplace=True)
        return dataframe


    def application(self):
        df = pd.read_csv(r'./home-credit-default-risk/application_train.csv')
        test_df = pd.read_csv(r'./home-credit-default-risk/application_test.csv')
        df = df.append(test_df).reset_index()


        # -----------------------------2022/06/30-----------------------------#
        # Remove some empty features
        #df.drop(['FLAG_DOCUMENT_2', 'FLAG_DOCUMENT_10', 'FLAG_DOCUMENT_12', 'FLAG_DOCUMENT_13', 'FLAG_DOCUMENT_14', 
        #        'FLAG_DOCUMENT_15', 'FLAG_DOCUMENT_16', 'FLAG_DOCUMENT_17', 'FLAG_DOCUMENT_19', 'FLAG_DOCUMENT_20', 
        #        'FLAG_DOCUMENT_21', 
        #        'EMERGENCYSTATE_MODE', 'FONDKAPREMONT_MODE', 'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE'], axis = 1, inplace = True)
        # -----------------------------2022/06/30-----------------------------#


        ##################################################################
        # カテゴリ変数の整備
        # （主に出現頻度が少ないカテゴリを整備していく）
        ##################################################################

        # -----------------------------2022/07/04-----------------------------#
        # 収入区分（NAME_INCOME_TYPE）は全部で8区分あるが、うち4区分は件数が小さい（30件以下）ため、
        # 近い意味合いのクラスに併合してしまうこととする。
        df.loc[df['NAME_INCOME_TYPE'] == 'Businessman', 'NAME_INCOME_TYPE'] = 'Commercial associate'
        df.loc[df['NAME_INCOME_TYPE'] == 'Maternity leave', 'NAME_INCOME_TYPE'] = 'Pensioner'
        df.loc[df['NAME_INCOME_TYPE'] == 'Student', 'NAME_INCOME_TYPE'] = 'State servant'
        df.loc[df['NAME_INCOME_TYPE'] == 'Unemployed', 'NAME_INCOME_TYPE'] = 'Pensioner'

        # 組織区分（ORGANIZATION_TYPE）は区分が多すぎるため、
        # 頻度の小さいものは併合して整理することとする。
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].str.contains("Business Entity"), 
        "Business_Entity", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].str.contains("Industry"), 
        "Industry", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].str.contains("Trade"),
        "Trade", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].str.contains("Transport"),
        "Transport", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["School", "Kindergarten", "University"]),
        "Education", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["Emergency","Police", "Medicine","Goverment", "Postal", "Military", "Security Ministries", "Legal Services"]),
        "Official", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["Bank", "Insurance"]),
        "Finance", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].str.contains("Goverment"), 
        "Government", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["Realtor", "Housing"]),
        "Realty", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["Hotel", "Restaurant","Services"]),
        "TourismFoodSector", df["ORGANIZATION_TYPE"])
        df["ORGANIZATION_TYPE"] = np.where(df["ORGANIZATION_TYPE"].isin(["Cleaning","Electricity", "Telecom", "Mobile", "Advertising", "Religion", "Culture"]),
        "Other", df["ORGANIZATION_TYPE"])

        # 職業区分（OCCUPATION_TYPE）は区分が多すぎるため、
        # 頻度の小さいものは併合して整理することとする。
        df["OCCUPATION_TYPE"] = np.where(df["OCCUPATION_TYPE"].isin(["Low-skill Laborers", "Cooking staff", "Security staff", "Private service staff", "Cleaning staff", "Waiters/barmen staff"]),
        "Low_skill_staff", df["OCCUPATION_TYPE"])
        df["OCCUPATION_TYPE"] = np.where(df["OCCUPATION_TYPE"].isin(["IT staff", "High skill tech staff"]),
        "High_skill_staff", df["OCCUPATION_TYPE"])
        df["OCCUPATION_TYPE"] = np.where(df["OCCUPATION_TYPE"].isin(["Secretaries", "HR staff","Realty agents"]),
        "Others", df["OCCUPATION_TYPE"])

        # 申込様式（NAME_TYPE_SUITE）は細かい区分が存在するが、構成比1%を切るものは全て Rare としてまとめる。
        # また、Spouse, partner は スペースが入っていて使いづらいので改名しておく。
        tmp = df["NAME_TYPE_SUITE"].value_counts() / len(df)
        rare_labels = tmp[tmp < 0.01].index
        df["NAME_TYPE_SUITE"] = np.where(df["NAME_TYPE_SUITE"].isin(rare_labels), 'Rare', df["NAME_TYPE_SUITE"])
        del tmp
        gc.collect()
        df["NAME_TYPE_SUITE"] = np.where(df["NAME_TYPE_SUITE"].str.contains("Spouse, partner"),
        "Spouse_partner", df["NAME_TYPE_SUITE"])

        # 学歴区分（NAME_EDUCATION_TYPE）のうち「Academic degree」は頻度が低いので、
        # Higher education に併合して整理することとする。
        # また、Secondary / secondary special は スペースが入っていて使いづらいので改名しておく。
        df["NAME_EDUCATION_TYPE"] = np.where(df["NAME_EDUCATION_TYPE"] == "Academic degree",
        "Higher education", df["NAME_EDUCATION_TYPE"])
        df["NAME_EDUCATION_TYPE"] = np.where(df["NAME_EDUCATION_TYPE"].str.contains("Secondary / secondary special"),
        "Secondary_secondary_special", df["ORGANIZATION_TYPE"])

        # NAME_FAMILY_STATUS の Single / not married は スペースが入っていて使いづらいので改名しておく。
        df["NAME_FAMILY_STATUS"] = np.where(df["NAME_FAMILY_STATUS"].str.contains("Single / not married"),
        "Single_not_married", df["NAME_FAMILY_STATUS"])

        # NAME_HOUSING_TYPE の House / apartment は スペースが入っていて使いづらいので改名しておく。
        df["NAME_HOUSING_TYPE"] = np.where(df["NAME_HOUSING_TYPE"].str.contains("House / apartment"),
        "House_apartment", df["NAME_HOUSING_TYPE"])

        # 地域フラグ（REG_〇〇）についてはフラグが 1 となっているカラム数を総計した NEW_REGION という変数を作成した。
        # 元の変数は削除する事とした。
        cols = ["REG_REGION_NOT_LIVE_REGION","REG_REGION_NOT_WORK_REGION", "LIVE_REGION_NOT_WORK_REGION", 
        "REG_CITY_NOT_LIVE_CITY","REG_CITY_NOT_WORK_CITY","LIVE_CITY_NOT_WORK_CITY"]
        df["NEW_REGION"] = df[cols].sum(axis = 1)
        df.drop(cols, axis = 1, inplace = True)

        # 提出書類フラグ（FLAG_DOC_〇〇）についてはフラグが 1 となっているカラム数を総計した NEW_DOCUMENT という変数を作成した。
        # 元の変数は削除する事とした。
        docs = [col for col in df.columns if 'FLAG_DOC' in col]
        df['NEW_DOCUMENT'] = df[docs].sum(axis=1)
        df.drop(docs, axis = 1, inplace = True)

        # 申請日時の情報（WEEKDAY_APPR_PROCESS_START と HOUR_APPR_PROCESS_START）については
        # 元の変数は残しつつも、周期エンコーディングを実行した。
        # （曜日・時刻を半径1の円周上に配置し、その座標を変数とする）
        weekday_dict = {'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7}
        df.replace({'WEEKDAY_APPR_PROCESS_START': weekday_dict}, inplace=True)
        df['NEW_WEEKDAY_APPR_PROCESS_START' + "_SIN"] = np.sin(2 * np.pi * df["WEEKDAY_APPR_PROCESS_START"]/7)
        df["NEW_WEEKDAY_APPR_PROCESS_START" + "_COS"] = np.cos(2 * np.pi * df["WEEKDAY_APPR_PROCESS_START"]/7)
        df['NEW_HOUR_APPR_PROCESS_START' + "_SIN"] = np.sin(2 * np.pi * df["HOUR_APPR_PROCESS_START"]/23)
        df["NEW_HOUR_APPR_PROCESS_START" + "_COS"] = np.cos(2 * np.pi * df["HOUR_APPR_PROCESS_START"]/23)
        # -----------------------------2022/07/04-----------------------------#





        # general cleaning procedures
        df = df[df['CODE_GENDER'] != 'XNA']
        df = df[df['AMT_INCOME_TOTAL'] < 20000000] # remove a outlier 117M
        # NaN values for DAYS_EMPLOYED: 365.243 -> nan
        df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace=True) # set null value
        df['DAYS_LAST_PHONE_CHANGE'].replace(0, np.nan, inplace=True) # set null value

        # Categorical features with Binary encode (0 or 1; two categories)
        for bin_feature in ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']:
            df[bin_feature], uniques = pd.factorize(df[bin_feature])
        
        # Categorical features with One-Hot encode
        df, cat_cols = self.one_hot_encoder(df, self.nan_as_category)

        # Flag_document features - count and kurtosis
        docs = [f for f in df.columns if 'FLAG_DOC' in f]
        df['DOCUMENT_COUNT'] = df[docs].sum(axis=1)
        df['NEW_DOC_KURT'] = df[docs].kurtosis(axis=1)

        def get_age_label(days_birth):
            """ Return the age group label (int). """
            age_years = -days_birth / 365
            if age_years < 27: return 1
            elif age_years < 40: return 2
            elif age_years < 50: return 3
            elif age_years < 65: return 4
            elif age_years < 99: return 5
            else: return 0
        # Categorical age - based on target=1 plot
        df['AGE_RANGE'] = df['DAYS_BIRTH'].apply(lambda x: get_age_label(x))

        # New features based on External sources
        df['EXT_SOURCES_PROD'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2'] * df['EXT_SOURCE_3']
        df['EXT_SOURCES_WEIGHTED'] = df.EXT_SOURCE_1 * 2 + df.EXT_SOURCE_2 * 1 + df.EXT_SOURCE_3 * 3
        np.warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        for function_name in ['min', 'max', 'mean', 'nanmedian', 'var']:
            feature_name = 'EXT_SOURCES_{}'.format(function_name.upper())
            df[feature_name] = eval('np.{}'.format(function_name))(
                df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']], axis=1)

        # Some simple new features (percentages)
        df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
        df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
        df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
        df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
        df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']

        # Credit ratios
        df['CREDIT_TO_GOODS_RATIO'] = df['AMT_CREDIT'] / df['AMT_GOODS_PRICE']
        
        # Income ratios
        df['INCOME_TO_EMPLOYED_RATIO'] = df['AMT_INCOME_TOTAL'] / df['DAYS_EMPLOYED']
        df['INCOME_TO_BIRTH_RATIO'] = df['AMT_INCOME_TOTAL'] / df['DAYS_BIRTH']
        
        # Time ratios
        df['ID_TO_BIRTH_RATIO'] = df['DAYS_ID_PUBLISH'] / df['DAYS_BIRTH']
        df['CAR_TO_BIRTH_RATIO'] = df['OWN_CAR_AGE'] / df['DAYS_BIRTH']
        df['CAR_TO_EMPLOYED_RATIO'] = df['OWN_CAR_AGE'] / df['DAYS_EMPLOYED']
        df['PHONE_TO_BIRTH_RATIO'] = df['DAYS_LAST_PHONE_CHANGE'] / df['DAYS_BIRTH']

        # EXT_SOURCE_X FEATURE
        df['APPS_EXT_SOURCE_MEAN'] = df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].mean(axis=1)
        df['APPS_EXT_SOURCE_STD'] = df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].std(axis=1)
        df['APPS_EXT_SOURCE_STD'] = df['APPS_EXT_SOURCE_STD'].fillna(df['APPS_EXT_SOURCE_STD'].mean())
        df['APP_SCORE1_TO_BIRTH_RATIO'] = df['EXT_SOURCE_1'] / (df['DAYS_BIRTH'] / 365.25)
        df['APP_SCORE2_TO_BIRTH_RATIO'] = df['EXT_SOURCE_2'] / (df['DAYS_BIRTH'] / 365.25)
        df['APP_SCORE3_TO_BIRTH_RATIO'] = df['EXT_SOURCE_3'] / (df['DAYS_BIRTH'] / 365.25)
        df['APP_SCORE1_TO_EMPLOY_RATIO'] = df['EXT_SOURCE_1'] / (df['DAYS_EMPLOYED'] / 365.25)
        df['APP_EXT_SOURCE_2*EXT_SOURCE_3*DAYS_BIRTH'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2'] * df['DAYS_BIRTH']
        df['APP_SCORE1_TO_FAM_CNT_RATIO'] = df['EXT_SOURCE_1'] / df['CNT_FAM_MEMBERS']
        df['APP_SCORE1_TO_GOODS_RATIO'] = df['EXT_SOURCE_1'] / df['AMT_GOODS_PRICE']
        df['APP_SCORE1_TO_CREDIT_RATIO'] = df['EXT_SOURCE_1'] / df['AMT_CREDIT']
        df['APP_SCORE1_TO_SCORE2_RATIO'] = df['EXT_SOURCE_1'] / df['EXT_SOURCE_2']
        df['APP_SCORE1_TO_SCORE3_RATIO'] = df['EXT_SOURCE_1'] / df['EXT_SOURCE_3']
        df['APP_SCORE2_TO_CREDIT_RATIO'] = df['EXT_SOURCE_2'] / df['AMT_CREDIT']
        df['APP_SCORE2_TO_REGION_RATING_RATIO'] = df['EXT_SOURCE_2'] / df['REGION_RATING_CLIENT']
        df['APP_SCORE2_TO_CITY_RATING_RATIO'] = df['EXT_SOURCE_2'] / df['REGION_RATING_CLIENT_W_CITY']
        df['APP_SCORE2_TO_POP_RATIO'] = df['EXT_SOURCE_2'] / df['REGION_POPULATION_RELATIVE']
        df['APP_SCORE2_TO_PHONE_CHANGE_RATIO'] = df['EXT_SOURCE_2'] / df['DAYS_LAST_PHONE_CHANGE']
        df['APP_EXT_SOURCE_1*EXT_SOURCE_2'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_2']
        df['APP_EXT_SOURCE_1*EXT_SOURCE_3'] = df['EXT_SOURCE_1'] * df['EXT_SOURCE_3']
        df['APP_EXT_SOURCE_2*EXT_SOURCE_3'] = df['EXT_SOURCE_2'] * df['EXT_SOURCE_3']
        df['APP_EXT_SOURCE_1*DAYS_EMPLOYED'] = df['EXT_SOURCE_1'] * df['DAYS_EMPLOYED']
        df['APP_EXT_SOURCE_2*DAYS_EMPLOYED'] = df['EXT_SOURCE_2'] * df['DAYS_EMPLOYED']
        df['APP_EXT_SOURCE_3*DAYS_EMPLOYED'] = df['EXT_SOURCE_3'] * df['DAYS_EMPLOYED']

        # AMT_INCOME_TOTAL : income
        # CNT_FAM_MEMBERS  : the number of family members
        df['APPS_GOODS_INCOME_RATIO'] = df['AMT_GOODS_PRICE'] / df['AMT_INCOME_TOTAL']
        df['APPS_CNT_FAM_INCOME_RATIO'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
        
        # DAYS_BIRTH : Client's age in days at the time of application
        # DAYS_EMPLOYED : How many days before the application the person started current employment
        df['APPS_INCOME_EMPLOYED_RATIO'] = df['AMT_INCOME_TOTAL'] / df['DAYS_EMPLOYED']

        # other feature from better than 0.8
        df['CREDIT_TO_GOODS_RATIO_2'] = df['AMT_CREDIT'] / df['AMT_GOODS_PRICE']
        df['APP_AMT_INCOME_TOTAL_12_AMT_ANNUITY_ratio'] = df['AMT_INCOME_TOTAL'] / 12. - df['AMT_ANNUITY']
        df['APP_INCOME_TO_EMPLOYED_RATIO'] = df['AMT_INCOME_TOTAL'] / df['DAYS_EMPLOYED']
        df['APP_DAYS_LAST_PHONE_CHANGE_DAYS_EMPLOYED_ratio'] = df['DAYS_LAST_PHONE_CHANGE'] / df['DAYS_EMPLOYED']
        df['APP_DAYS_EMPLOYED_DAYS_BIRTH_diff'] = df['DAYS_EMPLOYED'] - df['DAYS_BIRTH']

        print('"Application_Train_Test" final shape:', df.shape)
        return df

    
    def bureau_bb(self):
        bureau = pd.read_csv(r'./home-credit-default-risk/bureau.csv')
        bb = pd.read_csv(r'./home-credit-default-risk/bureau_balance.csv')

        # Credit duration and credit/account end date difference
        bureau['CREDIT_DURATION'] = -bureau['DAYS_CREDIT'] + bureau['DAYS_CREDIT_ENDDATE']
        bureau['ENDDATE_DIF'] = bureau['DAYS_CREDIT_ENDDATE'] - bureau['DAYS_ENDDATE_FACT']
        
        # Credit to debt ratio and difference
        bureau['DEBT_PERCENTAGE'] = bureau['AMT_CREDIT_SUM'] / bureau['AMT_CREDIT_SUM_DEBT']
        bureau['DEBT_CREDIT_DIFF'] = bureau['AMT_CREDIT_SUM'] - bureau['AMT_CREDIT_SUM_DEBT']
        bureau['CREDIT_TO_ANNUITY_RATIO'] = bureau['AMT_CREDIT_SUM'] / bureau['AMT_ANNUITY']
        bureau['BUREAU_CREDIT_FACT_DIFF'] = bureau['DAYS_CREDIT'] - bureau['DAYS_ENDDATE_FACT']
        bureau['BUREAU_CREDIT_ENDDATE_DIFF'] = bureau['DAYS_CREDIT'] - bureau['DAYS_CREDIT_ENDDATE']
        bureau['BUREAU_CREDIT_DEBT_RATIO'] = bureau['AMT_CREDIT_SUM_DEBT'] / bureau['AMT_CREDIT_SUM']

        # CREDIT_DAY_OVERDUE :
        bureau['BUREAU_IS_DPD'] = bureau['CREDIT_DAY_OVERDUE'].apply(lambda x: 1 if x > 0 else 0)
        bureau['BUREAU_IS_DPD_OVER120'] = bureau['CREDIT_DAY_OVERDUE'].apply(lambda x: 1 if x > 120 else 0)

        bb, bb_cat = self.one_hot_encoder(bb, self.nan_as_category)
        bureau, bureau_cat = self.one_hot_encoder(bureau, self.nan_as_category)

        # Bureau balance: Perform aggregations and merge with bureau.csv
        bb_aggregations = {'MONTHS_BALANCE': ['min', 'max', 'size', 'mean']}
        for col in bb_cat:
            bb_aggregations[col] = ['mean']

        #Status of Credit Bureau loan during the month
        bb_agg = bb.groupby('SK_ID_BUREAU').agg(bb_aggregations)
        bb_agg.columns = pd.Index([e[0] + "_" + e[1].upper() for e in bb_agg.columns.tolist()])
        bureau = bureau.join(bb_agg, how='left', on='SK_ID_BUREAU')

        # Bureau and bureau_balance numeric features
        num_aggregations = {
            'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],
            'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],
            'DAYS_CREDIT_UPDATE': ['mean'],
            'CREDIT_DAY_OVERDUE': ['max', 'mean', 'min'],
            'AMT_CREDIT_MAX_OVERDUE': ['mean', 'max'],
            'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],
            'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],
            'AMT_CREDIT_SUM_OVERDUE': ['mean', 'max', 'sum'],
            'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],
            'AMT_ANNUITY': ['max', 'mean', 'sum'],
            'CNT_CREDIT_PROLONG': ['sum'],
            'MONTHS_BALANCE_MIN': ['min'],
            'MONTHS_BALANCE_MAX': ['max'],
            'MONTHS_BALANCE_SIZE': ['mean', 'sum'],
            'SK_ID_BUREAU': ['count'],
            'DAYS_ENDDATE_FACT': ['min', 'max', 'mean'],
            'ENDDATE_DIF': ['min', 'max', 'mean'],
            'BUREAU_CREDIT_FACT_DIFF': ['min', 'max', 'mean'],
            'BUREAU_CREDIT_ENDDATE_DIFF': ['min', 'max', 'mean'],
            'BUREAU_CREDIT_DEBT_RATIO': ['min', 'max', 'mean'],
            'DEBT_CREDIT_DIFF': ['min', 'max', 'mean'],
            'BUREAU_IS_DPD': ['mean', 'sum'],
            'BUREAU_IS_DPD_OVER120': ['mean', 'sum']
            }

        # Bureau and bureau_balance categorical features
        cat_aggregations = {}
        for cat in bureau_cat: cat_aggregations[cat] = ['mean']
        for cat in bb_cat: cat_aggregations[cat + "_MEAN"] = ['mean']
        bureau_agg = bureau.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
        bureau_agg.columns = pd.Index(['BURO_' + e[0] + "_" + e[1].upper() for e in bureau_agg.columns.tolist()])

        # Bureau: Active credits - using only numerical aggregations
        active = bureau[bureau['CREDIT_ACTIVE_Active'] == 1]
        active_agg = active.groupby('SK_ID_CURR').agg(num_aggregations)
        active_agg.columns = pd.Index(['ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
        bureau_agg = bureau_agg.join(active_agg, how='left', on='SK_ID_CURR')

        # Bureau: Closed credits - using only numerical aggregations
        closed = bureau[bureau['CREDIT_ACTIVE_Closed'] == 1]
        closed_agg = closed.groupby('SK_ID_CURR').agg(num_aggregations)
        closed_agg.columns = pd.Index(['CLOSED_' + e[0] + "_" + e[1].upper() for e in closed_agg.columns.tolist()])
        bureau_agg = bureau_agg.join(closed_agg, how='left', on='SK_ID_CURR')

        print('"Bureau/Bureau Balance" final shape:', bureau_agg.shape)
        return bureau_agg

    
    def previous_application(self):
        prev = pd.read_csv(r'./home-credit-default-risk/previous_application.csv')

        prev, cat_cols = self.one_hot_encoder(prev, nan_as_category=True)

        # Days 365.243 values -> nan
        prev['DAYS_FIRST_DRAWING'].replace(365243, np.nan, inplace=True)
        prev['DAYS_FIRST_DUE'].replace(365243, np.nan, inplace=True)
        prev['DAYS_LAST_DUE_1ST_VERSION'].replace(365243, np.nan, inplace=True)
        prev['DAYS_LAST_DUE'].replace(365243, np.nan, inplace=True)
        prev['DAYS_TERMINATION'].replace(365243, np.nan, inplace=True)

        # Add feature: value ask / value received percentage
        prev['APP_CREDIT_PERC'] = prev['AMT_APPLICATION'] / prev['AMT_CREDIT']

        # Feature engineering: ratios and difference
        prev['APPLICATION_CREDIT_DIFF'] = prev['AMT_APPLICATION'] - prev['AMT_CREDIT']
        prev['CREDIT_TO_ANNUITY_RATIO'] = prev['AMT_CREDIT'] / prev['AMT_ANNUITY']
        prev['DOWN_PAYMENT_TO_CREDIT'] = prev['AMT_DOWN_PAYMENT'] / prev['AMT_CREDIT']

        # Interest ratio on previous application (simplified)
        total_payment = prev['AMT_ANNUITY'] * prev['CNT_PAYMENT']
        prev['SIMPLE_INTERESTS'] = (total_payment / prev['AMT_CREDIT'] - 1) / prev['CNT_PAYMENT']

        # Days last due difference (scheduled x done)
        prev['DAYS_LAST_DUE_DIFF'] = prev['DAYS_LAST_DUE_1ST_VERSION'] - prev['DAYS_LAST_DUE']

        # from off
        prev['PREV_GOODS_DIFF'] = prev['AMT_APPLICATION'] - prev['AMT_GOODS_PRICE']
        prev['PREV_ANNUITY_APPL_RATIO'] = prev['AMT_ANNUITY']/prev['AMT_APPLICATION']
        prev['PREV_GOODS_APPL_RATIO'] = prev['AMT_GOODS_PRICE'] / prev['AMT_APPLICATION']

        # Previous applications numeric features
        num_aggregations = {
            'AMT_ANNUITY': ['min', 'max', 'mean', 'sum'],
            'AMT_APPLICATION': ['min', 'max', 'mean', 'sum'],
            'AMT_CREDIT': ['min', 'max', 'mean', 'sum'],
            'APP_CREDIT_PERC': ['min', 'max', 'mean', 'var'],
            'AMT_DOWN_PAYMENT': ['min', 'max', 'mean', 'sum'],
            'AMT_GOODS_PRICE': ['min', 'max', 'mean', 'sum'],
            'HOUR_APPR_PROCESS_START': ['min', 'max', 'mean'],
            'RATE_DOWN_PAYMENT': ['min', 'max', 'mean'],
            'DAYS_DECISION': ['min', 'max', 'mean'],
            'CNT_PAYMENT': ['mean', 'sum'],
            'SK_ID_PREV': ['nunique'],
            'DAYS_TERMINATION': ['max'],
            'CREDIT_TO_ANNUITY_RATIO': ['mean', 'max'],
            'APPLICATION_CREDIT_DIFF': ['min', 'max', 'mean', 'sum'],
            'DOWN_PAYMENT_TO_CREDIT': ['mean'],
            'PREV_GOODS_DIFF': ['mean', 'max', 'sum'],
            'PREV_GOODS_APPL_RATIO': ['mean', 'max'],
            'DAYS_LAST_DUE_DIFF': ['mean', 'max', 'sum'],
            'SIMPLE_INTERESTS': ['mean', 'max']
        }

        # Previous applications categorical features
        cat_aggregations = {}
        for cat in cat_cols:
            cat_aggregations[cat] = ['mean']

        prev_agg = prev.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
        prev_agg.columns = pd.Index(['PREV_' + e[0] + "_" + e[1].upper() for e in prev_agg.columns.tolist()])

        # Previous Applications: Approved Applications - only numerical features
        approved = prev[prev['NAME_CONTRACT_STATUS_Approved'] == 1]
        approved_agg = approved.groupby('SK_ID_CURR').agg(num_aggregations)
        approved_agg.columns = pd.Index(['APPROVED_' + e[0] + "_" + e[1].upper() for e in approved_agg.columns.tolist()])
        prev_agg = prev_agg.join(approved_agg, how='left', on='SK_ID_CURR')

        # Previous Applications: Refused Applications - only numerical features
        refused = prev[prev['NAME_CONTRACT_STATUS_Refused'] == 1]
        refused_agg = refused.groupby('SK_ID_CURR').agg(num_aggregations)
        refused_agg.columns = pd.Index(['REFUSED_' + e[0] + "_" + e[1].upper() for e in refused_agg.columns.tolist()])
        prev_agg = prev_agg.join(refused_agg, how='left', on='SK_ID_CURR')

        print('"Previous Applications" final shape:', prev_agg.shape)
        return prev_agg

    
    def pos_cash(self):
        pos = pd.read_csv(r'./home-credit-default-risk/POS_CASH_balance.csv')

        pos, cat_cols = self.one_hot_encoder(pos, nan_as_category=True)

        # Flag months with late payment
        pos['LATE_PAYMENT'] = pos['SK_DPD'].apply(lambda x: 1 if x > 0 else 0)
        pos['POS_IS_DPD'] = pos['SK_DPD'].apply(lambda x: 1 if x > 0 else 0) # <-- same with ['LATE_PAYMENT']
        pos['POS_IS_DPD_UNDER_120'] = pos['SK_DPD'].apply(lambda x: 1 if (x > 0) & (x < 120) else 0)
        pos['POS_IS_DPD_OVER_120'] = pos['SK_DPD'].apply(lambda x: 1 if x >= 120 else 0)

        # Features
        aggregations = {
            'MONTHS_BALANCE': ['max', 'mean', 'size', 'min'],
            'SK_DPD': ['max', 'mean', 'sum', 'var', 'min'],
            'SK_DPD_DEF': ['max', 'mean', 'sum'],
            'SK_ID_PREV': ['nunique'],
            'LATE_PAYMENT': ['mean'],
            'SK_ID_CURR': ['count'],
            'CNT_INSTALMENT': ['min', 'max', 'mean', 'sum'],
            'CNT_INSTALMENT_FUTURE': ['min', 'max', 'mean', 'sum'],
            'POS_IS_DPD': ['mean', 'sum'],
            'POS_IS_DPD_UNDER_120': ['mean', 'sum'],
            'POS_IS_DPD_OVER_120': ['mean', 'sum'],
        }

        for cat in cat_cols:
            aggregations[cat] = ['mean']

        pos_agg = pos.groupby('SK_ID_CURR').agg(aggregations)
        pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in pos_agg.columns.tolist()])

        # Count pos cash accounts
        pos_agg['POS_COUNT'] = pos.groupby('SK_ID_CURR').size()


        sort_pos = pos.sort_values(by=['SK_ID_PREV', 'MONTHS_BALANCE'])
        gp = sort_pos.groupby('SK_ID_PREV')
        df_pos = pd.DataFrame()
        df_pos['SK_ID_CURR'] = gp['SK_ID_CURR'].first()
        df_pos['MONTHS_BALANCE_MAX'] = gp['MONTHS_BALANCE'].max()

        # Percentage of previous loans completed and completed before initial term
        df_pos['POS_LOAN_COMPLETED_MEAN'] = gp['NAME_CONTRACT_STATUS_Completed'].mean()
        df_pos['POS_COMPLETED_BEFORE_MEAN'] = gp['CNT_INSTALMENT'].first() - gp['CNT_INSTALMENT'].last()
        df_pos['POS_COMPLETED_BEFORE_MEAN'] = df_pos.apply(lambda x: 1 if x['POS_COMPLETED_BEFORE_MEAN'] > 0 \
                                                                        and x['POS_LOAN_COMPLETED_MEAN'] > 0 else 0, axis=1)
        # Number of remaining installments (future installments) and percentage from total
        df_pos['POS_REMAINING_INSTALMENTS'] = gp['CNT_INSTALMENT_FUTURE'].last()
        df_pos['POS_REMAINING_INSTALMENTS_RATIO'] = gp['CNT_INSTALMENT_FUTURE'].last()/gp['CNT_INSTALMENT'].last()

        # Group by SK_ID_CURR and merge
        df_gp = df_pos.groupby('SK_ID_CURR').sum().reset_index()
        df_gp.drop(['MONTHS_BALANCE_MAX'], axis=1, inplace= True)
        pos_agg = pd.merge(pos_agg, df_gp, on= 'SK_ID_CURR', how= 'left')

        # Percentage of late payments for the 3 most recent applications
        pos = self.do_sum(pos, ['SK_ID_PREV'], 'LATE_PAYMENT', 'LATE_PAYMENT_SUM')

        # Last month of each application
        last_month_df = pos.groupby('SK_ID_PREV')['MONTHS_BALANCE'].idxmax()

        # Most recent applications (last 3)
        sort_pos = pos.sort_values(by=['SK_ID_PREV', 'MONTHS_BALANCE'])
        gp = sort_pos.iloc[last_month_df].groupby('SK_ID_CURR').tail(3)
        gp_mean = gp.groupby('SK_ID_CURR').mean().reset_index()
        pos_agg = pd.merge(pos_agg, gp_mean[['SK_ID_CURR', 'LATE_PAYMENT_SUM']], on='SK_ID_CURR', how='left')

        print('"Pos-Cash" balance final shape:', pos_agg.shape) 
        return pos_agg


    def installment(self):
        ins = pd.read_csv(r'./home-credit-default-risk/installments_payments.csv')

        ins, cat_cols = self.one_hot_encoder(ins, nan_as_category=True)

        # Group payments and get Payment difference
        ins = self.do_sum(ins, ['SK_ID_PREV', 'NUM_INSTALMENT_NUMBER'], 'AMT_PAYMENT', 'AMT_PAYMENT_GROUPED')
        ins['PAYMENT_DIFFERENCE'] = ins['AMT_INSTALMENT'] - ins['AMT_PAYMENT_GROUPED']
        ins['PAYMENT_RATIO'] = ins['AMT_INSTALMENT'] / ins['AMT_PAYMENT_GROUPED']
        ins['PAID_OVER_AMOUNT'] = ins['AMT_PAYMENT'] - ins['AMT_INSTALMENT']
        ins['PAID_OVER'] = (ins['PAID_OVER_AMOUNT'] > 0).astype(int)

        # Percentage and difference paid in each installment (amount paid and installment value)
        ins['PAYMENT_PERC'] = ins['AMT_PAYMENT'] / ins['AMT_INSTALMENT']
        ins['PAYMENT_DIFF'] = ins['AMT_INSTALMENT'] - ins['AMT_PAYMENT']

        # Days past due and days before due (no negative values)
        ins['DPD_diff'] = ins['DAYS_ENTRY_PAYMENT'] - ins['DAYS_INSTALMENT']
        ins['DBD_diff'] = ins['DAYS_INSTALMENT'] - ins['DAYS_ENTRY_PAYMENT']
        ins['DPD'] = ins['DPD_diff'].apply(lambda x: x if x > 0 else 0)
        ins['DBD'] = ins['DBD_diff'].apply(lambda x: x if x > 0 else 0)

        # Flag late payment
        ins['LATE_PAYMENT'] = ins['DBD'].apply(lambda x: 1 if x > 0 else 0)
        ins['INSTALMENT_PAYMENT_RATIO'] = ins['AMT_PAYMENT'] / ins['AMT_INSTALMENT']
        ins['LATE_PAYMENT_RATIO'] = ins.apply(lambda x: x['INSTALMENT_PAYMENT_RATIO'] if x['LATE_PAYMENT'] == 1 else 0, axis=1)

        # Flag late payments that have a significant amount
        ins['SIGNIFICANT_LATE_PAYMENT'] = ins['LATE_PAYMENT_RATIO'].apply(lambda x: 1 if x > 0.05 else 0)
        
        # Flag k threshold late payments
        ins['DPD_7'] = ins['DPD'].apply(lambda x: 1 if x >= 7 else 0)
        ins['DPD_15'] = ins['DPD'].apply(lambda x: 1 if x >= 15 else 0)

        ins['INS_IS_DPD_UNDER_120'] = ins['DPD'].apply(lambda x: 1 if (x > 0) & (x < 120) else 0)
        ins['INS_IS_DPD_OVER_120'] = ins['DPD'].apply(lambda x: 1 if (x >= 120) else 0)

        # Features: Perform aggregations
        aggregations = {
            'NUM_INSTALMENT_VERSION': ['nunique'],
            'DPD': ['max', 'mean', 'sum', 'var'],
            'DBD': ['max', 'mean', 'sum', 'var'],
            'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],
            'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],
            'AMT_INSTALMENT': ['max', 'mean', 'sum', 'min'],
            'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],
            'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum', 'min'],
            'SK_ID_PREV': ['size', 'nunique'],
            'PAYMENT_DIFFERENCE': ['mean'],
            'PAYMENT_RATIO': ['mean', 'max'],
            'LATE_PAYMENT': ['mean', 'sum'],
            'SIGNIFICANT_LATE_PAYMENT': ['mean', 'sum'],
            'LATE_PAYMENT_RATIO': ['mean'],
            'DPD_7': ['mean'],
            'DPD_15': ['mean'],
            'PAID_OVER': ['mean'],
            'DPD_diff':['mean', 'min', 'max'],
            'DBD_diff':['mean', 'min', 'max'],
            'DAYS_INSTALMENT': ['mean', 'max', 'sum'],
            'INS_IS_DPD_UNDER_120': ['mean', 'sum'],
            'INS_IS_DPD_OVER_120': ['mean', 'sum']
        }

        for cat in cat_cols:
            aggregations[cat] = ['mean']
        ins_agg = ins.groupby('SK_ID_CURR').agg(aggregations)
        ins_agg.columns = pd.Index(['INSTAL_' + e[0] + "_" + e[1].upper() for e in ins_agg.columns.tolist()])

        # Count installments accounts
        ins_agg['INSTAL_COUNT'] = ins.groupby('SK_ID_CURR').size()

        # from oof (DAYS_ENTRY_PAYMENT)
        cond_day = ins['DAYS_ENTRY_PAYMENT'] >= -365
        ins_d365_grp = ins[cond_day].groupby('SK_ID_CURR')
        ins_d365_agg_dict = {
            'SK_ID_CURR': ['count'],
            'NUM_INSTALMENT_VERSION': ['nunique'],
            'DAYS_ENTRY_PAYMENT': ['mean', 'max', 'sum'],
            'DAYS_INSTALMENT': ['mean', 'max', 'sum'],
            'AMT_INSTALMENT': ['mean', 'max', 'sum'],
            'AMT_PAYMENT': ['mean', 'max', 'sum'],
            'PAYMENT_DIFF': ['mean', 'min', 'max', 'sum'],
            'PAYMENT_PERC': ['mean', 'max'],
            'DPD_diff': ['mean', 'min', 'max'],
            'DPD': ['mean', 'sum'],
            'INS_IS_DPD_UNDER_120': ['mean', 'sum'],
            'INS_IS_DPD_OVER_120': ['mean', 'sum']}

        ins_d365_agg = ins_d365_grp.agg(ins_d365_agg_dict)
        ins_d365_agg.columns = ['INS_D365' + ('_').join(column).upper() for column in ins_d365_agg.columns.ravel()]

        ins_agg = ins_agg.merge(ins_d365_agg, on='SK_ID_CURR', how='left')

        print('"Installments Payments" final shape:', ins_agg.shape)
        return ins_agg


    def credit_card(self):
        cc = pd.read_csv(r'./home-credit-default-risk/credit_card_balance.csv')

        cc, cat_cols = self.one_hot_encoder(cc, nan_as_category=True)

        # Amount used from limit
        cc['LIMIT_USE'] = cc['AMT_BALANCE'] / cc['AMT_CREDIT_LIMIT_ACTUAL']
        # Current payment / Min payment
        cc['PAYMENT_DIV_MIN'] = cc['AMT_PAYMENT_CURRENT'] / cc['AMT_INST_MIN_REGULARITY']
        # Late payment <-- 'CARD_IS_DPD'
        cc['LATE_PAYMENT'] = cc['SK_DPD'].apply(lambda x: 1 if x > 0 else 0)
        # How much drawing of limit
        cc['DRAWING_LIMIT_RATIO'] = cc['AMT_DRAWINGS_ATM_CURRENT'] / cc['AMT_CREDIT_LIMIT_ACTUAL']

        cc['CARD_IS_DPD_UNDER_120'] = cc['SK_DPD'].apply(lambda x: 1 if (x > 0) & (x < 120) else 0)
        cc['CARD_IS_DPD_OVER_120'] = cc['SK_DPD'].apply(lambda x: 1 if x >= 120 else 0)

        # General aggregations
        cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])
        cc_agg.columns = pd.Index(['CC_' + e[0] + "_" + e[1].upper() for e in cc_agg.columns.tolist()])

        # Count credit card lines
        cc_agg['CC_COUNT'] = cc.groupby('SK_ID_CURR').size()

        # Last month balance of each credit card application
        last_ids = cc.groupby('SK_ID_PREV')['MONTHS_BALANCE'].idxmax()
        last_months_df = cc[cc.index.isin(last_ids)]
        cc_agg = self.group_and_merge(last_months_df,cc_agg,'CC_LAST_', {'AMT_BALANCE': ['mean', 'max']})

        CREDIT_CARD_TIME_AGG = {
            'AMT_BALANCE': ['mean', 'max'],
            'LIMIT_USE': ['max', 'mean'],
            'AMT_CREDIT_LIMIT_ACTUAL':['max'],
            'AMT_DRAWINGS_ATM_CURRENT': ['max', 'sum'],
            'AMT_DRAWINGS_CURRENT': ['max', 'sum'],
            'AMT_DRAWINGS_POS_CURRENT': ['max', 'sum'],
            'AMT_INST_MIN_REGULARITY': ['max', 'mean'],
            'AMT_PAYMENT_TOTAL_CURRENT': ['max','sum'],
            'AMT_TOTAL_RECEIVABLE': ['max', 'mean'],
            'CNT_DRAWINGS_ATM_CURRENT': ['max','sum', 'mean'],
            'CNT_DRAWINGS_CURRENT': ['max', 'mean', 'sum'],
            'CNT_DRAWINGS_POS_CURRENT': ['mean'],
            'SK_DPD': ['mean', 'max', 'sum'],
            'LIMIT_USE': ['min', 'max'],
            'DRAWING_LIMIT_RATIO': ['min', 'max'],
            'LATE_PAYMENT': ['mean', 'sum'],
            'CARD_IS_DPD_UNDER_120': ['mean', 'sum'],
            'CARD_IS_DPD_OVER_120': ['mean', 'sum']
        }

        for months in [12, 24, 48]:
            cc_prev_id = cc[cc['MONTHS_BALANCE'] >= -months]['SK_ID_PREV'].unique()
            cc_recent = cc[cc['SK_ID_PREV'].isin(cc_prev_id)]
            prefix = 'INS_{}M_'.format(months)
            cc_agg = self.group_and_merge(cc_recent, cc_agg, prefix, CREDIT_CARD_TIME_AGG)


        print('"Credit Card Balance" final shape:', cc_agg.shape)
        return cc_agg


    def data_post_processing(self, dataframe):
        print(f'---=> the DATA POST-PROCESSING is beginning, the dataset has {dataframe.shape[1]} features')
        # keep index related columns
        index_cols = ['TARGET', 'SK_ID_CURR', 'SK_ID_BUREAU', 'SK_ID_PREV', 'index']

        dataframe = dataframe.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))
        print('names of feature are renamed')

        # Reduced memory usage
        dataframe = self.reduce_mem_usage(dataframe)
        print(f'---=> pandas data types of features in the dataset are converted for a reduced memory usage')

        # Remove non-informative columns
        noninformative_cols = []
        for col in dataframe.columns:
            if len(dataframe[col].value_counts()) < 2:
                noninformative_cols.append(col)

        dataframe.drop(noninformative_cols, axis=1, inplace=True)
        print(f'---=> {dataframe.shape[1]} features are remained after removing non-informative features')

        # Removing features not interesting for classifier
        feature_num = dataframe.shape[1]
        #this function does not work reason of insufficient memory, I added selected_feature manually!
        auc_limit = 0.7
        dataframe = self.ligthgbm_feature_selection(dataframe, index_cols, auc_limit)
        #all_features = dataframe.columns.tolist()
        #selected_feature_df = pd.read_csv('./homecredit-best-subs/removed_cols_lgbm.csv')
        #selected_features = selected_feature_df.removed_cols.tolist()
        #remained_features = set(all_features).difference(set(selected_features))
        #dataframe = dataframe[remained_features]
        print(f'{feature_num - dataframe.shape[1]} features are eliminated by LightGBM classifier with an {auc_limit} auc score limit in step I')
        print(f'---=> {dataframe.shape[1]} features are remained after removing features not interesting for LightGBM classifier')


        # generate new columns with risk_groupanizer
        start_feats_num = dataframe.shape[1]
        cat_cols = [col for col in dataframe.columns if 3 < len(dataframe[col].value_counts()) < 20 and col not in index_cols]
        dataframe, _ = self.risk_groupanizer(dataframe, column_names=cat_cols, upper_limit_ratio=8.1, lower_limit_ratio=8.1)
        print(f'---=> {dataframe.shape[1] - start_feats_num} features are generated with the risk_groupanizer')


        # ending message of DATA POST-PROCESSING
        print(f'---=> the DATA POST-PROCESSING is ended!, now the dataset has a total {dataframe.shape[1]} features')

        gc.collect()
        return dataframe