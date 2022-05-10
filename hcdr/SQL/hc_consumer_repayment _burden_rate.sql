SELECT 
at2.sk_id_curr 
-- ,pa.sk_id_prev 
-- ,pa.name_contract_status 
-- ,IFNULL(pa.amt_annuity, '0') as amt_annuity
,(sum(pa.amt_annuity)/at2.amt_income_total) as hc_consumer_repayment_burden_rate
-- ,ip.days_instalment 
-- ,ip.num_instalment_number 
-- ,ip.num_instalment_version 
FROM application_train at2 
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
INNER JOIN installments_payments ip 
ON pa.sk_id_curr = ip.sk_id_curr 
AND pa.sk_id_prev = ip.sk_id_prev 
WHERE 
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
at2.name_contract_type = "Cash loans"
AND pa.name_contract_type = "Consumer loans"
AND pa.flag_last_appl_per_contract = "Y"
AND pa.name_contract_status <> 'Refused'
AND ip.days_instalment >= -30
AND ip.num_instalment_version <> 0
GROUP BY ip.num_instalment_number,pa.sk_id_prev,at2.sk_id_curr 
ORDER BY at2.sk_id_curr