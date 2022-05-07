/**
 * Loan From Home Credit(Credit(Revolving))
 * */
/**
 * Loan From Home Credit(Cash / Consumer)
 * ê\ÇµçûÇ›åé
 * */
SELECT 
/* app_train */
at2.sk_id_curr
-- ,at2.target 
,at2.name_contract_type
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
,IFNULL(sum(pa.amt_annuity), '0.0') as sum_amt_annuity
,IFNULL(sum(pa.amt_application), '0.0') as sum_amt_application
,IFNULL(sum(pa.amt_credit), '0.0') as sum_amt_credit 
,IFNULL(sum(pa.amt_down_payment), '0.0') as sum_amt_down_payment
,IFNULL(sum(pa.amt_goods_price), '0') as sum_amt_goods_price
-- ,pa.weekday_appr_process_start
-- ,pa.hour_appr_process_start
-- ,pa.flag_last_appl_per_contract
-- ,pa.nflag_last_appl_in_day
,IFNULL(sum(pa.rate_down_payment), '0.0') as sum_rate_down_payment
,IFNULL(avg(pa.rate_interest_primary), '0.0') as avg_rate_interest_primary
,IFNULL(avg(pa.rate_interest_privileged), '0.0') as rate_interest_privileged
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
,IFNULL(max(pcb.sk_dpd), '0') as max_sk_dpd 
-- ,pcb.sk_dpd_def
FROM application_train at2
-- FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
/* POS */
INNER JOIN pos_cash_balance pcb 
ON pa.sk_id_prev = pcb.sk_id_prev 
AND pa.sk_id_curr = pcb.sk_id_curr
WHERE 
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
-- at2.name_contract_type = "Cash loans"
at2.name_contract_type = "Revolving loans"
AND pa.flag_last_appl_per_contract = "Y"
/*AND (pcb.name_contract_status = 'Completed' 
    OR pcb.name_contract_status = 'Canceled' 
    OR pcb.name_contract_status = 'Amortized debt')*/
AND pcb.months_balance = -1
GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr,pa.sk_id_prev,pcb.months_balance
;
