/**
 * Loan From Home Credit(Cash loans)
 * installment_payment_ratio_1000_mean_mean
 * nstallment payments�̒���DAYS_INSTALLMENT>-1000�̂��̂������o���AAMT_PAYMENT - AMT_INSTALMENT�̕��ς��Ƃ���
 * �ŏ���SK_ID_PREV��group by���A����SK_ID_CURR��group by����
 * */
SELECT 
at2.sk_id_curr
-- ,pa.sk_id_prev
,avg(ip.amt_payment - ip.amt_instalment) as installment_payment_ratio_1000_mean_mean
FROM application_train at2
-- FROM application_test at2
INNER JOIN previous_application pa 
ON at2.sk_id_curr = pa.sk_id_curr
INNER JOIN installments_payments ip 
ON pa.sk_id_curr = ip.sk_id_curr 
AND pa.sk_id_prev = ip.sk_id_prev
WHERE 
-- (pa.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
at2.name_contract_type = "Cash loans"
AND pa.name_contract_type = "Cash loans"
AND ip.days_instalment > -1000
GROUP BY at2.sk_id_curr
-- ORDER BY at2.sk_id_curr
;