/**
 * previous_applicationÇÃÇ›Çåãçá
 * prev_PRODUCT_COMBINATION
 * àÍî‘íºãﬂÇÃâûïÂÇÃì¡í•ó 
 * (loan_from_hc_cash)Ç÷à⁄ä«
 * */
SELECT 
/* app_train */
at2.sk_id_curr
,at2.target 
,at2.name_contract_type
,pa.sk_id_prev 
-- ,pa.name_contract_type as pa_name_contract_type
,pa.weekday_appr_process_start
,pa.hour_appr_process_start
-- ,pa.flag_last_appl_per_contract
,pa.nflag_last_appl_in_day
,pa.name_cash_loan_purpose
,pa.name_contract_status
,pa.name_cash_loan_purpose
,pa.name_contract_status
,pa.days_decision
,pa.name_payment_type
,pa.code_reject_reason
,IFNULL(pa.name_type_suite, 'NaN') as name_type_suite
,pa.name_client_type
,pa.name_goods_category
,pa.name_portfolio
,pa.name_product_type
,pa.channel_type
,pa.sellerplace_area
,pa.name_seller_industry
,IFNULL(pa.cnt_payment, '0') as cnt_payment
,pa.name_yield_group
,IFNULL(pa.product_combination, '0') as product_combination
,IFNULL(pa.days_first_drawing, '0') as days_first_drawing
,IFNULL(pa.days_first_due, '0') as days_first_due
,IFNULL(pa.days_last_due_1st_version, '0') as days_last_due_1st_version
,IFNULL(pa.days_last_due, '0') as days_last_due
,IFNULL(pa.days_termination, '0') as days_termination
,IFNULL(pa.nflag_insured_on_approval, '0') as nflag_insured_on_approval
FROM application_train at2
-- FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
INNER JOIN pos_cash_balance pcb 
ON pa.sk_id_prev = pcb.sk_id_prev 
	AND pa.sk_id_curr = pcb.sk_id_curr
INNER JOIN (
	SELECT
		app.sk_id_curr
		,max(pa2.hour_appr_process_start)
	FROM application_train app
	-- FROM application_test app
	INNER JOIN previous_application pa2 
		ON app.sk_id_curr = pa2.sk_id_curr
	WHERE app.name_contract_type = "Cash loans"
		AND pa2.name_contract_type = "Cash loans"
		AND pa2.flag_last_appl_per_contract = "Y"
	GROUP BY app.sk_id_curr
) as max_hour_appr_process_start
ON at2.sk_id_curr = max_hour_appr_process_start.sk_id_curr
WHERE at2.name_contract_type = "Cash loans"
AND pa.name_contract_type = "Cash loans"
AND pa.flag_last_appl_per_contract = "Y"
AND pcb.months_balance = -1
GROUP BY pa.sk_id_prev 
;