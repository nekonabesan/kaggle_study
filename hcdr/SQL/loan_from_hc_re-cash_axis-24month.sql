/**
 * Loan From Home Credit(Cash / Consumer)
 * 12‚©ŒŽ
 * */
SELECT 
/* app_train */
at2.sk_id_curr
-- ,at2.target
,truncate((abs(at2.days_birth) / 364.25), 0) as user_age
,(at2.days_registration - at2.days_birth) as unique_key_1
,(at2.days_id_publish - at2.days_birth) as unique_key_2
,case 
    when at2.code_gender = 'M' then 0
    when at2.code_gender = 'F' then 1
    else 2
end as gender_key
,count(at2.sk_id_curr) as value_count
-- ,at2.target 
-- ,at2.name_contract_type
-- ,pa.name_contract_type as pac
/*,at2.code_gender
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
-- ,pa.sk_id_prev 
-- ,pa.name_contract_type as pa_name_contract_type
,IFNULL(max(pa.amt_annuity), '0') as hc_re_cash_max_amt_annuity
,IFNULL(min(pa.amt_annuity), '0') as hc_re_cash_min_amt_annuity
,IFNULL(sum(pa.amt_annuity), '0') as hc_re_cash_sum_amt_annuity
,IFNULL(avg(pa.amt_annuity), '0') as hc_re_cash_avg_amt_annuity
,IFNULL(count(pa.amt_annuity), '0') as hc_re_cash_cnt_amt_annuity
,IFNULL(stddev(pa.amt_annuity), '0') as hc_re_cash_stddev_amt_annuity
,IFNULL(stddev_pop(pa.amt_annuity), '0') as hc_re_cash_stddev_pop_amt_annuity
,IFNULL(var_pop(pa.amt_annuity), '0') as hc_re_cash_var_pop_amt_annuity
,IFNULL(var_samp(pa.amt_annuity), '0') as hc_re_cash_var_samp_amt_annuity
,IFNULL(variance(pa.amt_annuity), '0') as hc_re_cash_variance_samp_amt_annuity

,IFNULL(max(pa.amt_application), '0') as hc_re_cash_max_amt_application
,IFNULL(min(pa.amt_application), '0') as hc_re_cash_min_amt_application
,IFNULL(sum(pa.amt_application), '0') as hc_re_cash_sum_amt_application
,IFNULL(avg(pa.amt_application), '0') as hc_re_cash_avg_amt_application
,IFNULL(count(pa.amt_application), '0') as hc_re_cash_cnt_amt_application
,IFNULL(stddev(pa.amt_application), '0') as hc_re_cash_stddev_amt_application
,IFNULL(stddev_pop(pa.amt_application), '0') as hc_re_cash_stddev_pop_amt_application
,IFNULL(var_pop(pa.amt_application), '0') as hc_re_cash_var_pop_amt_application
,IFNULL(var_samp(pa.amt_application), '0') as hc_re_cash_var_samp_amt_application
,IFNULL(variance(pa.amt_application), '0') as hc_re_cash_variance_samp_amt_application

,IFNULL(max(pa.amt_credit), '0') as hc_re_cash_max_amt_credit
,IFNULL(min(pa.amt_credit), '0') as hc_re_cash_min_amt_credit
,IFNULL(sum(pa.amt_credit), '0') as hc_re_cash_sum_amt_credit
,IFNULL(avg(pa.amt_credit), '0') as hc_re_cash_avg_amt_credit
,IFNULL(count(pa.amt_credit), '0') as hc_re_cash_cnt_amt_credit
,IFNULL(stddev(pa.amt_credit), '0') as hc_re_cash_stddev_amt_credit
,IFNULL(stddev_pop(pa.amt_credit), '0') as hc_re_cash_stddev_pop_amt_credit
,IFNULL(var_pop(pa.amt_credit), '0') as hc_re_cash_var_pop_amt_credit
,IFNULL(var_samp(pa.amt_credit), '0') as hc_re_cash_var_samp_amt_credit
,IFNULL(variance(pa.amt_credit), '0') as hc_re_cash_variance_samp_amt_credit

,IFNULL(max(pa.amt_down_payment), '0') as hc_re_cash_max_amt_down_payment
,IFNULL(min(pa.amt_down_payment), '0') as hc_re_cash_min_amt_down_payment
,IFNULL(sum(pa.amt_down_payment), '0') as hc_re_cash_sum_amt_down_payment
,IFNULL(avg(pa.amt_down_payment), '0') as hc_re_cash_avg_amt_down_payment
,IFNULL(count(pa.amt_down_payment), '0') as hc_re_cash_cnt_amt_down_payment
,IFNULL(stddev(pa.amt_down_payment), '0') as hc_re_cash_stddev_amt_down_payment
,IFNULL(stddev_pop(pa.amt_down_payment), '0') as hc_re_cash_stddev_pop_amt_down_payment
,IFNULL(var_pop(pa.amt_down_payment), '0') as hc_re_cash_var_pop_amt_down_payment
,IFNULL(var_samp(pa.amt_down_payment), '0') as hc_re_cash_var_samp_amt_down_payment
,IFNULL(variance(pa.amt_down_payment), '0') as hc_re_cash_variance_samp_amt_down_payment

,IFNULL(max(pa.amt_goods_price), '0') as hc_re_cash_max_amt_goods_price
,IFNULL(min(pa.amt_goods_price), '0') as hc_re_cash_min_amt_goods_price
,IFNULL(sum(pa.amt_goods_price), '0') as hc_re_cash_sum_amt_goods_price
,IFNULL(avg(pa.amt_goods_price), '0') as hc_re_cash_avg_amt_goods_price
,IFNULL(count(pa.amt_goods_price), '0') as hc_re_cash_cnt_amt_goods_price
,IFNULL(stddev(pa.amt_goods_price), '0') as hc_re_cash_stddev_amt_goods_price
,IFNULL(stddev_pop(pa.amt_goods_price), '0') as hc_re_cash_stddev_pop_amt_goods_price
,IFNULL(var_pop(pa.amt_goods_price), '0') as hc_re_cash_var_pop_amt_goods_price
,IFNULL(var_samp(pa.amt_goods_price), '0') as hc_re_cash_var_samp_amt_goods_price
,IFNULL(variance(pa.amt_goods_price), '0') as hc_re_cash_variance_samp_amt_goods_price
-- ,pa.weekday_appr_process_start
-- ,pa.hour_appr_process_start
-- ,pa.flag_last_appl_per_contract
-- ,pa.nflag_last_appl_in_day
,IFNULL(max(pa.rate_down_payment), '0') as hc_re_cash_max_rate_down_payment
,IFNULL(min(pa.rate_down_payment), '0') as hc_re_cash_min_rate_down_payment
,IFNULL(sum(pa.rate_down_payment), '0') as hc_re_cash_sum_rate_down_payment
,IFNULL(avg(pa.rate_down_payment), '0') as hc_re_cash_avg_rate_down_payment
,IFNULL(count(pa.rate_down_payment), '0') as hc_re_cash_cnt_rate_down_payment
,IFNULL(stddev(pa.rate_down_payment), '0') as hc_re_cash_stddev_rate_down_payment
,IFNULL(stddev_pop(pa.rate_down_payment), '0') as hc_re_cash_stddev_pop_rate_down_payment
,IFNULL(var_pop(pa.rate_down_payment), '0') as hc_re_cash_var_pop_rate_down_payment
,IFNULL(var_samp(pa.rate_down_payment), '0') as hc_re_cash_var_samp_rate_down_payment
,IFNULL(variance(pa.rate_down_payment), '0') as hc_re_cash_variance_samp_rate_down_payment

,IFNULL(max(pa.rate_interest_primary), '0') as hc_re_cash_max_rate_interest_primary
,IFNULL(min(pa.rate_interest_primary), '0') as hc_re_cash_min_rate_interest_primary
,IFNULL(sum(pa.rate_interest_primary), '0') as hc_re_cash_sum_rate_interest_primary
,IFNULL(avg(pa.rate_interest_primary), '0') as hc_re_cash_avg_rate_interest_primary
,IFNULL(count(pa.rate_interest_primary), '0') as hc_re_cash_cnt_rate_interest_primary
,IFNULL(stddev(pa.rate_interest_primary), '0') as hc_re_cash_stddev_rate_interest_primary
,IFNULL(stddev_pop(pa.rate_interest_primary), '0') as hc_re_cash_stddev_pop_rate_interest_primary
,IFNULL(var_pop(pa.rate_interest_primary), '0') as hc_re_cash_var_pop_rate_interest_primary
,IFNULL(var_samp(pa.rate_interest_primary), '0') as hc_re_cash_var_samp_rate_interest_primary
,IFNULL(variance(pa.rate_interest_primary), '0') as hc_re_cash_variance_samp_rate_interest_primary

,IFNULL(max(pa.rate_interest_privileged), '0') as hc_re_cash_max_rate_interest_privileged
,IFNULL(min(pa.rate_interest_privileged), '0') as hc_re_cash_min_rate_interest_privileged
,IFNULL(sum(pa.rate_interest_privileged), '0') as hc_re_cash_sum_rate_interest_privileged
,IFNULL(avg(pa.rate_interest_privileged), '0') as hc_re_cash_avg_rate_interest_privileged
,IFNULL(count(pa.rate_interest_privileged), '0') as hc_re_cash_cnt_rate_interest_privileged
,IFNULL(stddev(pa.rate_interest_privileged), '0') as hc_re_cash_stddev_rate_interest_privileged
,IFNULL(stddev_pop(pa.rate_interest_privileged), '0') as hc_re_cash_stddev_pop_rate_interest_privileged
,IFNULL(var_pop(pa.rate_interest_privileged), '0') as hc_re_cash_var_pop_rate_interest_privileged
,IFNULL(var_samp(pa.rate_interest_privileged), '0') as hc_re_cash_var_samp_rate_interest_privileged
,IFNULL(variance(pa.rate_interest_privileged), '0') as hc_re_cash_variance_samp_rate_interest_privileged

-- ,pa.name_cash_loan_purpose
-- ,pa.name_contract_status
-- ,pa.days_decision
-- ,pa.name_payment_type
-- ,pa.code_reject_reason
-- ,pa.name_type_suite
-- ,pa.name_client_type
-- ,pa.name_goods_category
-- ,pa.name_portfolio
-- ,pa.name_product_type
-- ,pa.channel_type
-- ,pa.sellerplace_area
-- ,pa.name_seller_industry
-- ,pa.cnt_payment
-- ,pa.name_yield_group
-- ,pa.product_combination
-- ,pa.days_first_drawing
-- ,pa.days_first_due
-- ,pa.days_last_due_1st_version
-- ,pa.days_last_due
-- ,pa.days_termination
-- ,pa.nflag_insured_on_approval
-- ,pcb.months_balance
-- ,pcb.cnt_instalment
-- ,pcb.cnt_instalment_future
-- ,pcb.name_contract_status
,IFNULL(max(pcb.sk_dpd), '0') as hc_re_cash_max_sk_dpd
,IFNULL(min(pcb.sk_dpd), '0') as hc_re_cash_min_sk_dpd
,IFNULL(sum(pcb.sk_dpd), '0') as hc_re_cash_sum_sk_dpd
,IFNULL(avg(pcb.sk_dpd), '0') as hc_re_cash_avg_sk_dpd
,IFNULL(count(pcb.sk_dpd), '0') as hc_re_cash_cnt_sk_dpd
,IFNULL(stddev(pcb.sk_dpd), '0') as hc_re_cash_stddev_sk_dpd
,IFNULL(stddev_pop(pcb.sk_dpd), '0') as hc_re_cash_stddev_pop_sk_dpd
,IFNULL(var_pop(pcb.sk_dpd), '0') as hc_re_cash_var_pop_sk_dpd
,IFNULL(var_samp(pcb.sk_dpd), '0') as hc_re_cash_var_samp_sk_dpd
,IFNULL(variance(pcb.sk_dpd), '0') as hc_re_cash_variance_samp_sk_dpd
-- ,pcb.sk_dpd_def
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
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
at2.name_contract_type = "Revolving loans"
-- Consumer loans OR Cash loans
AND pa.name_contract_type = "Cash loans"
-- AND pa.flag_last_appl_per_contract = "Y"
/*AND (pcb.name_contract_status = 'Completed' 
    OR pcb.name_contract_status = 'Canceled' 
    OR pcb.name_contract_status = 'Amortized debt')*/
AND abs(pcb.months_balance) <= 24
GROUP BY 
-- at2.sk_id_curr
unique_key_1
,unique_key_2
,code_gender
,region_population_relative
ORDER BY
unique_key_1 desc
,unique_key_2 desc
,code_gender
,region_population_relative
,user_age
,at2.sk_id_curr
,pa.sk_id_prev
,pcb.months_balance
;