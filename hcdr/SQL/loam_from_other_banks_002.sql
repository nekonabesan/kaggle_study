use `home-credit-default-risk`;
/**
 * Loan From other banks
 * */
SELECT 
at2.sk_id_curr
-- ,b.sk_id_bureau
-- ,at2.target 
/*,at2.name_contract_type
,at2.code_gender
,at2.flag_own_car
,at2.flag_own_realty
,at2.cnt_children
,at2.name_type_suite
,at2.name_income_type
,at2.name_education_type
,at2.name_family_status
,at2.name_housing_type
,at2.region_population_relative
,at2.days_birth
,at2.days_employed
,at2.own_car_age
,at2.occupation_type
,at2.cnt_fam_members
,at2.region_rating_client
,at2.region_rating_client_w_city
,at2.organization_type
,at2.ext_source_1
,at2.ext_source_2
,at2.ext_source_3*/
/**/
-- ,b.credit_active 
-- ,b.credit_currency 
-- (申込み月)申し込み時点での他金融機関ローンの延滞日数
,IFNULL(min(b.credit_day_overdue), '0') as br_min_credit_day_overdue
,IFNULL(max(b.credit_day_overdue), '0') as br_max_credit_day_overdue
,IFNULL(sum(b.credit_day_overdue), '0') as br_sum_credit_day_overdue
,IFNULL(avg(b.credit_day_overdue), '0') as br_avg_credit_day_overdue
,IFNULL(count(b.credit_day_overdue), '0') as br_cnt_credit_day_overdue
,IFNULL(stddev(b.credit_day_overdue), '0') as br_stddev_credit_day_overdue
,IFNULL(stddev_pop(b.credit_day_overdue), '0') as br_stddev_pop_credit_day_overdue
,IFNULL(var_pop(b.credit_day_overdue), '0') as br_var_pop_credit_day_overdue
,IFNULL(var_samp(b.credit_day_overdue), '0') as br_var_samp_credit_day_overdue
,IFNULL(variance(b.credit_day_overdue), '0') as br_variance_pop_credit_day_overdue
-- 申し込み時点での他金融機関ローンの残りの日数
,IFNULL(min(b.days_credit_enddate), '0') as br_min_days_credit_enddate
,IFNULL(max(b.days_credit_enddate), '0') as br_max_days_credit_enddate
,IFNULL(sum(b.days_credit_enddate), '0') as br_sum_days_credit_enddate
,IFNULL(avg(b.days_credit_enddate), '0') as br_avg_days_credit_enddate
,IFNULL(count(b.days_credit_enddate), '0') as br_cnt_days_credit_enddate
,IFNULL(stddev(b.days_credit_enddate), '0') as br_stddev_days_credit_enddate
,IFNULL(stddev_pop(b.days_credit_enddate), '0') as br_stddev_pop_days_credit_enddate
,IFNULL(var_pop(b.days_credit_enddate), '0') as br_var_pop_days_credit_enddate
,IFNULL(var_samp(b.days_credit_enddate), '0') as br_var_samp_days_credit_enddate
,IFNULL(variance(b.days_credit_enddate), '0') as br_variance_pop_days_credit_enddate
-- 申し込み時点での他金融機関ローンが払い終わっている場合の払い終わってからの日数
,IFNULL(min(b.days_enddate_fact), '0') as br_min_days_enddate_fact
,IFNULL(max(b.days_enddate_fact), '0') as br_max_days_enddate_fact
,IFNULL(sum(b.days_enddate_fact), '0') as br_sum_days_enddate_fact
,IFNULL(avg(b.days_enddate_fact), '0') as br_avg_days_enddate_fact
,IFNULL(count(b.days_enddate_fact), '0') as br_cnt_days_enddate_fact
,IFNULL(stddev(b.days_enddate_fact), '0') as br_stddev_days_enddate_fact
,IFNULL(stddev_pop(b.days_enddate_fact), '0') as br_stddev_pop_days_enddate_fact
,IFNULL(var_pop(b.days_enddate_fact), '0') as br_var_pop_days_enddate_fact
,IFNULL(var_samp(b.days_enddate_fact), '0') as br_var_samp_days_enddate_fact
,IFNULL(variance(b.days_enddate_fact), '0') as br_variance_pop_days_enddate_fact
 -- (申込み月)これまでの最大延滞金額
,IFNULL(min(b.amt_credit_max_overdue), '0') as br_min_amt_credit_max_overdue
,IFNULL(max(b.amt_credit_max_overdue), '0') as br_max_amt_credit_max_overdue
,IFNULL(sum(b.amt_credit_max_overdue), '0') as br_sum_amt_credit_max_overdue
,IFNULL(avg(b.amt_credit_max_overdue), '0') as br_avg_amt_credit_max_overdue
,IFNULL(count(b.amt_credit_max_overdue), '0') as br_cnt_amt_credit_max_overdue
,IFNULL(stddev(b.amt_credit_max_overdue), '0') as br_stddev_amt_credit_max_overdue
,IFNULL(stddev_pop(b.amt_credit_max_overdue), '0') as br_stddev_pop_amt_credit_max_overdue
,IFNULL(var_pop(b.amt_credit_max_overdue), '0') as br_var_pop_amt_credit_max_overdue
,IFNULL(var_samp(b.amt_credit_max_overdue), '0') as br_var_samp_amt_credit_max_overdue
,IFNULL(variance(b.amt_credit_max_overdue), '0') as br_variance_pop_amt_credit_max_overdue
-- (申込み月)クレジットを何回延長したか(件数)
,IFNULL(min(b.cnt_credit_prolong), '0') as br_min_cnt_credit_prolong
,IFNULL(max(b.cnt_credit_prolong), '0') as br_max_cnt_credit_prolong
,IFNULL(sum(b.cnt_credit_prolong), '0') as br_sum_cnt_credit_prolong
,IFNULL(avg(b.cnt_credit_prolong), '0') as br_avg_cnt_credit_prolong
,IFNULL(count(b.cnt_credit_prolong), '0') as br_cnt_cnt_credit_prolong
,IFNULL(stddev(b.cnt_credit_prolong), '0') as br_stddev_cnt_credit_prolong
,IFNULL(stddev_pop(b.cnt_credit_prolong), '0') as br_stddev_pop_cnt_credit_prolong
,IFNULL(var_pop(b.cnt_credit_prolong), '0') as br_var_pop_cnt_credit_prolong
,IFNULL(var_samp(b.cnt_credit_prolong), '0') as br_var_samp_cnt_credit_prolong
,IFNULL(variance(b.cnt_credit_prolong), '0') as br_variance_pop_cnt_credit_prolong
-- (申込み月)信用情報機関登録されている与信額の総和
,IFNULL(min(b.amt_credit_sum), '0') as br_min_amt_credit_sum
,IFNULL(max(b.amt_credit_sum), '0') as br_max_amt_credit_sum
,IFNULL(sum(b.amt_credit_sum), '0') as br_sum_amt_credit_sum
,IFNULL(avg(b.amt_credit_sum), '0') as br_avg_amt_credit_sum
,IFNULL(count(b.amt_credit_sum), '0') as br_cnt_amt_credit_sum
,IFNULL(stddev(b.amt_credit_sum), '0') as br_stddev_amt_credit_sum
,IFNULL(stddev_pop(b.amt_credit_sum), '0') as br_stddev_pop_amt_credit_sum
,IFNULL(var_pop(b.amt_credit_sum), '0') as br_var_pop_amt_credit_sum
,IFNULL(var_samp(b.amt_credit_sum), '0') as br_var_samp_amt_credit_sum
,IFNULL(variance(b.amt_credit_sum), '0') as br_variance_pop_amt_credit_sum
-- (申込み月)信用情報機関に登録されている債務
,IFNULL(min(b.amt_credit_sum_debt), '0') as br_min_amt_credit_sum_debt
,IFNULL(max(b.amt_credit_sum_debt), '0') as br_max_amt_credit_sum_debt
,IFNULL(sum(b.amt_credit_sum_debt), '0') as br_sum_amt_credit_sum_debt
,IFNULL(avg(b.amt_credit_sum_debt), '0') as br_avg_amt_credit_sum_debt
,IFNULL(count(b.amt_credit_sum_debt), '0') as br_cnt_amt_credit_sum_debt
,IFNULL(stddev(b.amt_credit_sum_debt), '0') as br_stddev_amt_credit_sum_debt
,IFNULL(stddev_pop(b.amt_credit_sum_debt), '0') as br_stddev_pop_amt_credit_sum_debt
,IFNULL(var_pop(b.amt_credit_sum_debt), '0') as br_var_pop_amt_credit_sum_debt
,IFNULL(var_samp(b.amt_credit_sum_debt), '0') as br_var_samp_amt_credit_sum_debt
,IFNULL(variance(b.amt_credit_sum_debt), '0') as br_variance_pop_amt_credit_sum_debt
-- (申込み月)信用情報機関に登録されているクレジットカードの限度額
,IFNULL(min(b.amt_credit_sum_limit), '0') as br_min_amt_credit_sum_limit
,IFNULL(max(b.amt_credit_sum_limit), '0') as br_max_amt_credit_sum_limit
,IFNULL(sum(b.amt_credit_sum_limit), '0') as br_sum_amt_credit_sum_limit
,IFNULL(avg(b.amt_credit_sum_limit), '0') as br_avg_amt_credit_sum_limit
,IFNULL(count(b.amt_credit_sum_limit), '0') as br_cnt_amt_credit_sum_limit
,IFNULL(stddev(b.amt_credit_sum_limit), '0') as br_stddev_amt_credit_sum_limit
,IFNULL(stddev_pop(b.amt_credit_sum_limit), '0') as br_stddev_pop_amt_credit_sum_limit
,IFNULL(var_pop(b.amt_credit_sum_limit), '0') as br_var_pop_amt_credit_sum_limit
,IFNULL(var_samp(b.amt_credit_sum_limit), '0') as br_var_samp_amt_credit_sum_limit
,IFNULL(variance(b.amt_credit_sum_limit), '0') as br_variance_pop_amt_credit_sum_limit  
-- (申込み月)信用情報機関に登録されているクレジットカードの残高(使用額)
,IFNULL(min(b.amt_credit_sum_overdue), '0') as br_min_amt_credit_sum_overdue
,IFNULL(max(b.amt_credit_sum_overdue), '0') as br_max_amt_credit_sum_overdue
,IFNULL(sum(b.amt_credit_sum_overdue), '0') as br_sum_amt_credit_sum_overdue
,IFNULL(avg(b.amt_credit_sum_overdue), '0') as br_avg_amt_credit_sum_overdue
,IFNULL(count(b.amt_credit_sum_overdue), '0') as br_cnt_amt_credit_sum_overdue
,IFNULL(stddev(b.amt_credit_sum_overdue), '0') as br_stddev_amt_credit_sum_overdue
,IFNULL(stddev_pop(b.amt_credit_sum_overdue), '0') as br_stddev_pop_amt_credit_sum_overdue
,IFNULL(var_pop(b.amt_credit_sum_overdue), '0') as br_var_pop_amt_credit_sum_overdue
,IFNULL(var_samp(b.amt_credit_sum_overdue), '0') as br_var_samp_amt_credit_sum_overdue
,IFNULL(variance(b.amt_credit_sum_overdue), '0') as br_variance_pop_amt_credit_sum_overdue
-- 申し込み日から、信用情報機関に最後に情報が登録された日までの日数
,IFNULL(min(b.days_credit_update), '0') as br_min_days_credit_update
,IFNULL(max(b.days_credit_update), '0') as br_max_days_credit_update
,IFNULL(sum(b.days_credit_update), '0') as br_sum_days_credit_update
,IFNULL(avg(b.days_credit_update), '0') as br_avg_days_credit_update
,IFNULL(count(b.days_credit_update), '0') as br_cnt_days_credit_update
,IFNULL(stddev(b.days_credit_update), '0') as br_stddev_days_credit_update
,IFNULL(stddev_pop(b.days_credit_update), '0') as br_stddev_pop_days_credit_update
,IFNULL(var_pop(b.days_credit_update), '0') as br_var_pop_days_credit_update
,IFNULL(var_samp(b.days_credit_update), '0') as br_var_samp_days_credit_update
,IFNULL(variance(b.days_credit_update), '0') as br_variance_pop_days_credit_update
-- 登録されているローン支払い額
,IFNULL(min(b.amt_annuity), '0') as br_min_amt_annuity
,IFNULL(max(b.amt_annuity), '0') as br_max_amt_annuity
,IFNULL(sum(b.amt_annuity), '0') as br_sum_amt_annuity
,IFNULL(avg(b.amt_annuity), '0') as br_avg_amt_annuity
,IFNULL(count(b.amt_annuity), '0') as br_cnt_amt_annuity
,IFNULL(stddev(b.amt_annuity), '0') as br_stddev_amt_annuity
,IFNULL(stddev_pop(b.amt_annuity), '0') as br_stddev_pop_amt_annuity
,IFNULL(var_pop(b.amt_annuity), '0') as br_var_pop_amt_annuity
,IFNULL(var_samp(b.amt_annuity), '0') as br_var_samp_amt_annuity
,IFNULL(variance(b.amt_annuity), '0') as br_variance_pop_amt_annuity
-- ,bb.months_balance 
-- ,bb.status
FROM application_train at2 
-- FROM application_test at2
LEFT JOIN bureau b
ON at2.sk_id_curr = b.sk_id_curr
LEFT JOIN  bureau_balance bb 
ON b.sk_id_bureau = bb.sk_id_bureau
-- ================================================================= --
-- Value Type Of b.credit_type
-- Consumer credit
-- Credit card
-- Mortgage
-- Car loan
-- Microloan
-- Loan for working capital replenishment
-- Loan for business development
-- Real estate loan
-- Unknown type of loan
-- Another type of loan
-- Cash loan (non-earmarked)
-- Loan for the purchase of equipment
-- Mobile operator loan
-- Interbank credit
-- Loan for purchase of shares (margin lending)
-- ================================================================= --
WHERE /*b.credit_type = "Consumer credit"   -- クレジットカード(ローン契約?)の種類 
-- AND bb.months_balance = 0
-- AND b.credit_type = "Credit card"   -- クレジットカード(ローン契約?)の種類
AND*/ ABS(bb.months_balance) <= 60          -- ローン申し込み日からの何か月前かの変数(-1であれば直近月を意味する)
-- AND b.days_credit_update >= -180 
GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr, b.sk_id_bureau, b.days_credit_update  
;