/**
 * Loan From Home Credit(Credit(Revolving))
 * prev_PRODUCT_COMBINATION
 * 一番直近の応募の特徴量
 * */
SELECT 
/* app_train */
at2.sk_id_curr
-- ,at2.target 
-- ,at2.name_contract_type as app_name_contract_type
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
,IFNULL(pa.amt_annuity, '0.0') as revo_amt_annuity
,IFNULL(pa.amt_application, '0.0') as revo_amt_application
,IFNULL(pa.amt_credit, '0.0') as revo_amt_credit 
,IFNULL(pa.amt_down_payment, '0.0') as revo_amt_down_payment
,IFNULL(pa.amt_goods_price, '0') as revo_amt_goods_price
,pa.weekday_appr_process_start as revo_weekday_appr_process_start
,pa.hour_appr_process_start as revo_hour_appr_process_start
,pa.flag_last_appl_per_contract as revo_flag_last_appl_per_contract
,pa.nflag_last_appl_in_day as revo_nflag_last_appl_in_day 
,IFNULL(pa.rate_down_payment, '0.0') as revo_rate_down_payment
,IFNULL(pa.rate_interest_primary, '0.0') as revo_rate_interest_primary
,IFNULL(pa.rate_interest_privileged, '0.0') as revo_rate_interest_privileged
,pa.name_cash_loan_purpose as revo_name_cash_loan_purpose
,pa.name_contract_status as revo_name_contract_status
,pa.days_decision as revo_days_decision
,pa.name_payment_type as revo_name_payment_type
,pa.code_reject_reason as revo_code_reject_reason
,pa.name_type_suite as revo_name_type_suite
,pa.name_client_type as revo_name_client_type
,pa.name_goods_category as revo_name_goods_category
,pa.name_portfolio as revo_name_portfolio
,pa.name_product_type as revo_name_product_type
,pa.channel_type as revo_channel_type
,pa.sellerplace_area as revo_sellerplace_area
,pa.name_seller_industry as revo_name_seller_industry
,pa.cnt_payment as revo_cnt_payment
,pa.name_yield_group as revo_name_yield_group
,pa.product_combination as revo_product_combination
,pa.days_first_drawing as revo_days_first_drawing
,pa.days_first_due as revo_days_first_due
,pa.days_last_due_1st_version as revo_days_last_due_1st_version
,pa.days_last_due as revo_days_last_due
,pa.days_termination as revo_days_termination
,pa.nflag_insured_on_approval as revo_nflag_insured_on_approval
,IFNULL(max(ccb.sk_dpd), '0') as revo_max_sk_dpd
FROM application_train at2
-- FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
/* POS */
INNER JOIN credit_card_balance ccb 
ON pa.sk_id_prev = ccb.sk_id_prev 
AND pa.sk_id_curr = ccb.sk_id_curr
INNER JOIN installments_payments ip 
ON pa.sk_id_curr = ip.sk_id_curr 
AND pa.sk_id_prev = ip.sk_id_prev
WHERE 
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
/*at2.name_contract_type = "Revolving loans"
-- AND*/ pa.name_contract_type = "Revolving loans"
AND pa.flag_last_appl_per_contract = "Y"
AND ccb.months_balance = -1
-- クレジットカード
AND ip.num_instalment_version = 0
GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr,pa.sk_id_prev,ccb.months_balance
;