/**
 * Loan From Home Credit(Cash loans)
 * prev_PRODUCT_COMBINATION
 * Nか月
 * */
SELECT 
at2.sk_id_curr
-- ,at2.target 
-- AMT_ANNUITY|ローン支払い額|
,ROUND(IFNULL(min(pa.amt_annuity), '0'), 5) as hc_all_min_amt_annuity
,IFNULL(max(pa.amt_annuity), '0') as hc_all_max_amt_annuity
,IFNULL(sum(pa.amt_annuity), '0') as hc_all_sum_amt_annuity
,IFNULL(avg(pa.amt_annuity), '0') as hc_all_avg_amt_annuity
,IFNULL(count(pa.amt_annuity), '0') as hc_all_cnt_amt_annuity
,IFNULL(stddev(pa.amt_annuity), '0') as hc_all_stddev_amt_annuity
,IFNULL(stddev_pop(pa.amt_annuity), '0') as hc_all_stddev_pop_amt_annuity
,IFNULL(var_pop(pa.amt_annuity), '0') as hc_all_var_pop_amt_annuity
,IFNULL(var_samp(pa.amt_annuity), '0') as hc_all_var_samp_amt_annuity
,IFNULL(variance(pa.amt_annuity), '0') as hc_all_variance_pop_amt_annuity
-- AMT_APPLICATION|借り入れ申し込み金額|
,IFNULL(min(pa.amt_application), '0') as hc_all_min_amt_application
,IFNULL(max(pa.amt_application), '0') as hc_all_max_amt_application
,IFNULL(sum(pa.amt_application), '0') as hc_all_sum_amt_application
,IFNULL(avg(pa.amt_application), '0') as hc_all_avg_amt_application
,IFNULL(count(pa.amt_application), '0') as hc_all_cnt_amt_application
,IFNULL(stddev(pa.amt_application), '0') as hc_all_stddev_amt_application
,IFNULL(stddev_pop(pa.amt_application), '0') as hc_all_stddev_pop_amt_application
,IFNULL(var_pop(pa.amt_application), '0') as hc_all_var_pop_amt_application
,IFNULL(var_samp(pa.amt_application), '0') as hc_all_var_samp_amt_application
,IFNULL(variance(pa.amt_application), '0') as hc_all_variance_pop_amt_application
-- AMT_CREDIT|借り入れ承認金額(最終的な貸付金額)|
,IFNULL(min(pa.amt_credit), '0') as hc_all_min_amt_credit
,IFNULL(max(pa.amt_credit), '0') as hc_all_max_amt_credit
,IFNULL(sum(pa.amt_credit), '0') as hc_all_sum_amt_credit
,IFNULL(avg(pa.amt_credit), '0') as hc_all_avg_amt_credit
,IFNULL(count(pa.amt_credit), '0') as hc_all_cnt_amt_credit
,IFNULL(stddev(pa.amt_credit), '0') as hc_all_stddev_amt_credit
,IFNULL(stddev_pop(pa.amt_credit), '0') as hc_all_stddev_pop_amt_credit
,IFNULL(var_pop(pa.amt_credit), '0') as hc_all_var_pop_amt_credit
,IFNULL(var_samp(pa.amt_credit), '0') as hc_all_var_samp_amt_credit
,IFNULL(variance(pa.amt_credit), '0') as hc_all_variance_pop_amt_credit
-- AMT_DOWN_PAYMENT|頭金|
,IFNULL(min(pa.amt_down_payment), '0') as hc_all_min_amt_down_payment
,IFNULL(max(pa.amt_down_payment), '0') as hc_all_max_amt_down_payment
,IFNULL(sum(pa.amt_down_payment), '0') as hc_all_sum_amt_down_payment
,IFNULL(avg(pa.amt_down_payment), '0') as hc_all_avg_amt_down_payment
,IFNULL(count(pa.amt_down_payment), '0') as hc_all_cnt_amt_down_payment
,IFNULL(stddev(pa.amt_down_payment), '0') as hc_all_stddev_amt_down_payment
,IFNULL(stddev_pop(pa.amt_down_payment), '0') as hc_all_stddev_pop_amt_down_payment
,IFNULL(var_pop(pa.amt_down_payment), '0') as hc_all_var_pop_amt_down_payment
,IFNULL(var_samp(pa.amt_down_payment), '0') as hc_all_var_samp_amt_down_payment
-- AMT_GOODS_PRICE|クライアントが要求した商品価格|
,IFNULL(min(pa.amt_goods_price), '0') as hc_all_min_amt_goods_price
,IFNULL(max(pa.amt_goods_price), '0') as hc_all_max_amt_goods_price
,IFNULL(sum(pa.amt_goods_price), '0') as hc_all_sum_amt_goods_price
,IFNULL(avg(pa.amt_goods_price), '0') as hc_all_avg_amt_goods_price
,IFNULL(count(pa.amt_goods_price), '0') as hc_all_cnt_amt_goods_price
,IFNULL(stddev(pa.amt_goods_price), '0') as hc_all_stddev_amt_goods_price
,IFNULL(stddev_pop(pa.amt_goods_price), '0') as hc_all_stddev_pop_amt_goods_price
,IFNULL(var_pop(pa.amt_goods_price), '0') as hc_all_var_pop_amt_goods_price
,IFNULL(var_samp(pa.amt_goods_price), '0') as hc_all_var_samp_amt_goods_price
,IFNULL(variance(pa.amt_goods_price), '0') as hc_all_variance_pop_amt_goods_price
-- RATE_DOWN_PAYMENT|前払い率|
,IFNULL(min(pa.rate_down_payment), '0') as hc_all_min_rate_down_payment
,IFNULL(max(pa.rate_down_payment), '0') as hc_all_max_rate_down_payment
,IFNULL(sum(pa.rate_down_payment), '0') as hc_all_sum_rate_down_payment
,IFNULL(avg(pa.rate_down_payment), '0') as hc_all_avg_rate_down_payment
,IFNULL(count(pa.rate_down_payment), '0') as hc_all_cnt_rate_down_payment
,IFNULL(stddev(pa.rate_down_payment), '0') as hc_all_stddev_rate_down_payment
,IFNULL(stddev_pop(pa.rate_down_payment), '0') as hc_all_stddev_pop_rate_down_payment
,IFNULL(var_pop(pa.rate_down_payment), '0') as hc_all_var_pop_rate_down_payment
,IFNULL(var_samp(pa.rate_down_payment), '0') as hc_all_var_samp_rate_down_payment
,IFNULL(variance(pa.rate_down_payment), '0') as hc_all_variance_pop_rate_down_payment
-- RATE_INTEREST_PRIMARY|金利|
,IFNULL(min(pa.rate_interest_primary), '0') as hc_all_min_rate_interest_primary
,IFNULL(max(pa.rate_interest_primary), '0') as hc_all_max_rate_interest_primary
,IFNULL(sum(pa.rate_interest_primary), '0') as hc_all_sum_rate_interest_primary
,IFNULL(avg(pa.rate_interest_primary), '0') as hc_all_avg_rate_interest_primary
,IFNULL(count(pa.rate_interest_primary), '0') as hc_all_cnt_rate_interest_primary
,IFNULL(stddev(pa.rate_interest_primary), '0') as hc_all_stddev_rate_interest_primary
,IFNULL(stddev_pop(pa.rate_interest_primary), '0') as hc_all_stddev_pop_rate_interest_primary
,IFNULL(var_pop(pa.rate_interest_primary), '0') as hc_all_var_pop_rate_interest_primary
,IFNULL(var_samp(pa.rate_interest_primary), '0') as hc_all_var_samp_rate_interest_primary
,IFNULL(variance(pa.rate_interest_primary), '0') as hc_all_variance_pop_rate_interest_primary
-- RATE_INTEREST_PRIVILEGED|金利|
,IFNULL(min(pa.rate_interest_privileged), '0') as hc_all_min_rate_interest_privileged
,IFNULL(max(pa.rate_interest_privileged), '0') as hc_all_max_rate_interest_privileged
,IFNULL(sum(pa.rate_interest_privileged), '0') as hc_all_sum_rate_interest_privileged
,IFNULL(avg(pa.rate_interest_privileged), '0') as hc_all_avg_rate_interest_privileged
,IFNULL(count(pa.rate_interest_privileged), '0') as hc_all_cnt_rate_interest_privileged
,IFNULL(stddev(pa.rate_interest_privileged), '0') as hc_all_stddev_rate_interest_privileged
,IFNULL(stddev_pop(pa.rate_interest_privileged), '0') as hc_all_stddev_pop_rate_interest_privileged
,IFNULL(var_pop(pa.rate_interest_privileged), '0') as hc_all_var_pop_rate_interest_privileged
,IFNULL(var_samp(pa.rate_interest_privileged), '0') as hc_all_var_samp_rate_interest_privileged
,IFNULL(variance(pa.rate_interest_privileged), '0') as hc_all_variance_pop_rate_interest_privileged
-- DAYS_DECISION|今回申込日との日数差|
,IFNULL(min(pa.days_decision), '0') as hc_all_min_days_decision
,IFNULL(max(pa.days_decision), '0') as hc_all_max_days_decision
,IFNULL(sum(pa.days_decision), '0') as hc_all_sum_days_decision
,IFNULL(avg(pa.days_decision), '0') as hc_all_avg_days_decision
,IFNULL(count(pa.days_decision), '0') as hc_all_cnt_days_decision
,IFNULL(stddev(pa.days_decision), '0') as hc_all_stddev_days_decision
,IFNULL(stddev_pop(pa.days_decision), '0') as hc_all_stddev_pop_days_decision
,IFNULL(var_pop(pa.days_decision), '0') as hc_all_var_pop_days_decision
,IFNULL(var_samp(pa.days_decision), '0') as hc_all_var_samp_days_decision
,IFNULL(variance(pa.days_decision), '0') as hc_all_variance_pop_days_decision
-- 
,IFNULL(min(pa.cnt_payment), '0') as hc_all_min_cnt_payment
,IFNULL(max(pa.cnt_payment), '0') as hc_all_max_cnt_payment
,IFNULL(sum(pa.cnt_payment), '0') as hc_all_sum_cnt_payment
,IFNULL(avg(pa.cnt_payment), '0') as hc_all_avg_cnt_payment
,IFNULL(count(pa.cnt_payment), '0') as hc_all_cnt_cnt_payment
,IFNULL(stddev(pa.cnt_payment), '0') as hc_all_stddev_cnt_payment
,IFNULL(stddev_pop(pa.cnt_payment), '0') as hc_all_stddev_pop_cnt_payment
,IFNULL(var_pop(pa.cnt_payment), '0') as hc_all_var_pop_cnt_payment
,IFNULL(var_samp(pa.cnt_payment), '0') as hc_all_var_samp_cnt_payment
,IFNULL(variance(pa.cnt_payment), '0') as hc_all_variance_pop_cnt_payment
-- 
,IFNULL(min(pa.days_first_drawing), '0') as hc_all_min_days_first_drawing
,IFNULL(max(pa.days_first_drawing), '0') as hc_all_max_days_first_drawing
,IFNULL(sum(pa.days_first_drawing), '0') as hc_all_sum_days_first_drawing
,IFNULL(avg(pa.days_first_drawing), '0') as hc_all_avg_days_first_drawing
,IFNULL(count(pa.days_first_drawing), '0') as hc_all_cnt_days_first_drawing
,IFNULL(stddev(pa.days_first_drawing), '0') as hc_all_stddev_days_first_drawing
,IFNULL(stddev_pop(pa.days_first_drawing), '0') as hc_all_stddev_pop_days_first_drawing
,IFNULL(var_pop(pa.days_first_drawing), '0') as hc_all_var_pop_days_first_drawing
,IFNULL(var_samp(pa.days_first_drawing), '0') as hc_all_var_samp_days_first_drawing
,IFNULL(variance(pa.days_first_drawing), '0') as hc_all_variance_pop_days_first_drawing
-- 
,IFNULL(min(pa.days_first_due), '0') as hc_all_min_days_first_due
,IFNULL(max(pa.days_first_due), '0') as hc_all_max_days_first_due
,IFNULL(sum(pa.days_first_due), '0') as hc_all_sum_days_first_due
,IFNULL(avg(pa.days_first_due), '0') as hc_all_avg_days_first_due
,IFNULL(count(pa.days_first_due), '0') as hc_all_cnt_days_first_due
,IFNULL(stddev(pa.days_first_due), '0') as hc_all_stddev_days_first_due
,IFNULL(stddev_pop(pa.days_first_due), '0') as hc_all_stddev_pop_days_first_due
,IFNULL(var_pop(pa.days_first_due), '0') as hc_all_var_pop_days_first_due
,IFNULL(var_samp(pa.days_first_due), '0') as hc_all_var_samp_days_first_due
,IFNULL(variance(pa.days_first_due), '0') as hc_all_variance_pop_days_first_due
-- 
,IFNULL(min(pa.days_last_due_1st_version), '0') as hc_all_min_days_last_due_1st_version
,IFNULL(max(pa.days_last_due_1st_version), '0') as hc_all_max_days_last_due_1st_version
,IFNULL(sum(pa.days_last_due_1st_version), '0') as hc_all_sum_days_last_due_1st_version
,IFNULL(avg(pa.days_last_due_1st_version), '0') as hc_all_avg_days_last_due_1st_version
,IFNULL(count(pa.days_last_due_1st_version), '0') as hc_all_cnt_days_last_due_1st_version
,IFNULL(stddev(pa.days_last_due_1st_version), '0') as hc_all_stddev_days_last_due_1st_version
,IFNULL(stddev_pop(pa.days_last_due_1st_version), '0') as hc_all_stddev_pop_days_last_due_1st_version
,IFNULL(var_pop(pa.days_last_due_1st_version), '0') as hc_all_var_pop_days_last_due_1st_version
,IFNULL(var_samp(pa.days_last_due_1st_version), '0') as hc_all_var_samp_days_last_due_1st_version
,IFNULL(variance(pa.days_last_due_1st_version), '0') as hc_all_variance_pop_days_last_due_1st_version
-- 
,IFNULL(min(pa.days_last_due), '0') as hc_all_min_days_last_due
,IFNULL(max(pa.days_last_due), '0') as hc_all_max_days_last_due
,IFNULL(sum(pa.days_last_due), '0') as hc_all_sum_days_last_due
,IFNULL(avg(pa.days_last_due), '0') as hc_all_avg_days_last_due
,IFNULL(count(pa.days_last_due), '0') as hc_all_cnt_days_last_due
,IFNULL(stddev(pa.days_last_due), '0') as hc_all_stddev_days_last_due
,IFNULL(stddev_pop(pa.days_last_due), '0') as hc_all_stddev_pop_days_last_due
,IFNULL(var_pop(pa.days_last_due), '0') as hc_all_var_pop_days_last_due
,IFNULL(var_samp(pa.days_last_due), '0') as hc_all_var_samp_days_last_due
,IFNULL(variance(pa.days_last_due), '0') as hc_all_variance_pop_days_last_due
-- 
,IFNULL(min(pa.days_termination), '0') as hc_all_min_days_termination
,IFNULL(max(pa.days_termination), '0') as hc_all_max_days_termination
,IFNULL(sum(pa.days_termination), '0') as hc_all_sum_days_termination
,IFNULL(avg(pa.days_termination), '0') as hc_all_avg_days_termination
,IFNULL(count(pa.days_termination), '0') as hc_all_cnt_days_termination
,IFNULL(stddev(pa.days_termination), '0') as hc_all_stddev_days_termination
,IFNULL(stddev_pop(pa.days_termination), '0') as hc_all_stddev_pop_days_termination
,IFNULL(var_pop(pa.days_termination), '0') as hc_all_var_pop_days_termination
,IFNULL(var_samp(pa.days_termination), '0') as hc_all_var_samp_days_termination
,IFNULL(variance(pa.days_termination), '0') as hc_all_variance_pop_days_termination
-- 
,IFNULL(min(pcb.sk_dpd), '0') as hc_all_min_sk_dpd
,IFNULL(max(pcb.sk_dpd), '0') as hc_all_max_sk_dpd
,IFNULL(sum(pcb.sk_dpd), '0') as hc_all_sum_sk_dpd
,IFNULL(avg(pcb.sk_dpd), '0') as hc_all_avg_sk_dpd
,IFNULL(count(pcb.sk_dpd), '0') as hc_all_cnt_sk_dpd
,IFNULL(stddev(pcb.sk_dpd), '0') as hc_all_stddev_sk_dpd
,IFNULL(stddev_pop(pcb.sk_dpd), '0') as hc_all_stddev_pop_sk_dpd
,IFNULL(var_pop(pcb.sk_dpd), '0') as hc_all_var_pop_sk_dpd
,IFNULL(var_samp(pcb.sk_dpd), '0') as hc_all_var_samp_sk_dpd
,IFNULL(variance(pcb.sk_dpd), '0') as hc_all_variance_pop_sk_dpd
-- FROM application_train at2
FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
/* POS */
INNER JOIN pos_cash_balance pcb 
ON pa.sk_id_prev = pcb.sk_id_prev 
AND pa.sk_id_curr = pcb.sk_id_curr
INNER JOIN installments_payments ip 
ON pa.sk_id_curr = ip.sk_id_curr 
AND pa.sk_id_prev = ip.sk_id_prev
WHERE 
abs(pcb.months_balance) <= 12
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
-- at2.name_contract_type = "Cash loans"
-- AND pa.name_contract_type = "Cash loans"
-- AND pa.flag_last_appl_per_contract = "Y"
-- クレジットカードを除く
-- AND ip.num_instalment_version <> 0
GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr,pa.sk_id_prev,pcb.months_balance
;