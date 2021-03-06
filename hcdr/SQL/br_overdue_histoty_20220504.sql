SELECT 
    app.sk_id_curr 
    -- (全期間)他金融機関ローンの延滞日数
    ,IFNULL(max(b2.credit_day_overdue), '0') as hist_max_credit_day_overdue
	,IFNULL(count(b2.credit_day_overdue), '0') as hist_cnt_credit_day_overdue
    ,IFNULL(sum(b2.credit_day_overdue), '0') as hist_sum_credit_day_overdue
    -- (全期間)クレジットを何回延長したか
    ,IFNULL(max(b2.cnt_credit_prolong), '0') as hist_max_credit_prolong   -- 最大延長日数
    ,IFNULL(count(b2.cnt_credit_prolong), '0') as hist_cnt_credit_prolong -- 登録回数
	,IFNULL(sum(b2.cnt_credit_prolong), '0') as hist_sum_credit_prolong   -- 登録されている最大延長日数の合計
	-- これまでの最大延滞金額
	,IFNULL(max(b2.amt_credit_max_overdue), '0') as hist_max_amt_credit_max_overdue   -- 最大延滞金額 
	,IFNULL(count(b2.amt_credit_max_overdue), '0') as hist_cnt_amt_credit_max_overdue -- 延滞金額記録回数
	,IFNULL(sum(b2.amt_credit_max_overdue), '0') as hist_sum_amt_credit_max_overdue   -- 過去に登録された延滞金額の合計
FROM application_test app
LEFT JOIN bureau b2
	ON app.sk_id_curr = b2.sk_id_curr
LEFT JOIN  bureau_balance bb2 
	ON b2.sk_id_bureau = bb2.sk_id_bureau
	GROUP BY app.sk_id_curr;