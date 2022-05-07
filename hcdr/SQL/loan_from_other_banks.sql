use `home-credit-default-risk`;
/**
 * Loan From other banks
 * */
SELECT 
at2.sk_id_curr
,b.sk_id_bureau
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
,IFNULL(max(b.credit_day_overdue), '0') as max_credit_day_overdue   -- (申込み月)申し込み時点での他金融機関ローンの延滞日数
,IFNULL(max(b.days_credit_enddate), '0') as max_days_credit_enddate -- 申し込み時点での他金融機関ローンの残りの日数
,IFNULL(min(b.days_enddate_fact), '0') as min_days_enddate_fact     -- 申し込み時点での他金融機関ローンが払い終わっている場合の払い終わってからの日数
,IFNULL(max(b.amt_credit_max_overdue), '0') as max_amt_credit_max_overdue -- (申込み月)これまでの最大延滞金額
,IFNULL(count(b.cnt_credit_prolong), '0') as cnt_credit_prolong           -- (申込み月)クレジットを何回延長したか(件数)
,IFNULL(max(b.cnt_credit_prolong), '0') as max_credit_prolong             -- (申込み月)クレジットを何回延長したか(最大)
,IFNULL(sum(b.amt_credit_sum), '0') as sum_amt_credit_sum                 -- (申込み月)信用情報機関登録されている与信額の総和
,IFNULL(sum(b.amt_credit_sum_debt), '0') as sum_amt_credit_sum_debt       -- (申込み月)信用情報機関に登録されている債務
,IFNULL(sum(b.amt_credit_sum_limit), '0') as sum_amt_credit_sum_limit     -- (申込み月)信用情報機関に登録されているクレジットカードの限度額
,IFNULL(sum(b.amt_credit_sum_overdue), '0') as sum_amt_credit_sum_overdue -- (申込み月)信用情報機関に登録されているクレジットカードの残高(使用額)
,IFNULL(b.credit_type, 'NaN') as credit_type
,IFNULL(max(b.days_credit_update), '0') as max_days_credit_update         -- 申し込み日から、信用情報機関に最後に情報が登録された日までの日数
,IFNULL(sum(b.amt_annuity), '0.0') as sum_amt_annuity                     -- 登録されているローン支払い額
-- ,bb.months_balance 
-- ,bb.status
/*,hist.max_credit_day_overdue
,hist.cnt_credit_day_overdue
,hist.sum_credit_day_overdue
,hist.max_credit_prolong
,hist.cnt_credit_prolong
,hist.sum_credit_day_overdue
,hist.max_amt_credit_max_overdue
,hist.cnt_amt_credit_max_overdue
,hist.sum_amt_credit_max_overdue*/
FROM application_train at2 
-- FROM application_test at2
LEFT JOIN bureau b
ON at2.sk_id_curr = b.sk_id_curr
LEFT JOIN  bureau_balance bb 
ON b.sk_id_bureau = bb.sk_id_bureau
/*LEFT JOIN (
	SELECT 
	    app.sk_id_curr 
	    -- (全期間)他金融機関ローンの延滞日数
	    ,IFNULL(max(b2.credit_day_overdue), '0') as max_credit_day_overdue
		,IFNULL(count(b2.credit_day_overdue), '0') as cnt_credit_day_overdue
	    ,IFNULL(sum(b2.credit_day_overdue), '0') as sum_credit_day_overdue
	    -- (全期間)クレジットを何回延長したか
	    ,IFNULL(max(b2.cnt_credit_prolong), '0') as max_credit_prolong   -- 最大延長日数
	    ,IFNULL(count(b2.cnt_credit_prolong), '0') as cnt_credit_prolong -- 登録回数
		,IFNULL(sum(b2.cnt_credit_prolong), '0') as sum_credit_prolong   -- 登録されている最大延長日数の合計
		-- これまでの最大延滞金額
		,IFNULL(max(b2.amt_credit_max_overdue), '0') as max_amt_credit_max_overdue   -- 最大延滞金額 
		,IFNULL(count(b2.amt_credit_max_overdue), '0') as cnt_amt_credit_max_overdue -- 延滞金額記録回数
		,IFNULL(sum(b2.amt_credit_max_overdue), '0') as sum_amt_credit_max_overdue   -- 過去に登録された延滞金額の合計
	FROM application_trein app
	LEFT JOIN bureau b2
		ON app.sk_id_curr = b2.sk_id_curr
	LEFT JOIN  bureau_balance bb2 
		ON b2.sk_id_bureau = bb2.sk_id_bureau
	GROUP BY app.sk_id_curr
) as hist
ON at2.sk_id_curr = hist.sk_id_curr*/
-- ================================================================= --
-- Consumer credit
-- Credit card
-- Other, Car loan, Microlone ......
-- ================================================================= --
WHERE bb.months_balance = 0
-- AND b.credit_type = "Consumer credit"   -- クレジットカード(ローン契約?)の種類
-- AND ABS(bb.months_balance) <= 12          -- ローン申し込み日からの何か月前かの変数(-1であれば直近月を意味する)
-- AND b.days_credit_update >= -180 

GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr, b.sk_id_bureau, b.days_credit_update  
;