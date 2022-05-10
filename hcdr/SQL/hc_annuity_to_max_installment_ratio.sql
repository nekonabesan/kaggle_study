/**
 * annuity_to_max_installment_ratio
　* AMT_ANNUITY / (installments_paymentsをSK_ID_CURRでgroup byしたのち、最大のinstallment)
 * ローン支払い額 / 実際の支払日  - 申し込み日(基本マイナス)
 * */
SELECT 
/* app_train */
ip.sk_id_curr
,at2.amt_annuity/max(ip.days_instalment) as annuity_to_max_installment_ratio
-- FROM application_train at2
FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
/* POS */
INNER JOIN pos_cash_balance pcb 
ON pa.sk_id_prev = pcb.sk_id_prev 
AND pa.sk_id_curr = pcb.sk_id_curr
INNER JOIN installments_payments ip 
ON pcb.sk_id_prev = ip.sk_id_prev 
AND pcb.sk_id_curr = ip.sk_id_curr
WHERE 
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
at2.name_contract_type = "Cash loans"
-- at2.name_contract_type = "Revolving loans"
AND pa.name_contract_type = "Cash loans"
AND pa.flag_last_appl_per_contract = "Y"
/*AND (pcb.name_contract_status = 'Completed' 
    OR pcb.name_contract_status = 'Canceled' 
    OR pcb.name_contract_status = 'Amortized debt')*/
AND pcb.months_balance = -1
GROUP BY ip.sk_id_curr
ORDER BY ip.sk_id_curr,ip.sk_id_prev,pcb.months_balance
;
