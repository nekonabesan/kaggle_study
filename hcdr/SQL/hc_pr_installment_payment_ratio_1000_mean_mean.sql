/**
 * Loan From Home Credit(Cash loans)
 * installment_payment_ratio_1000_mean_mean
 * nstallment payments‚Ì’†‚ÅDAYS_INSTALLMENT>-1000‚Ì‚à‚Ì‚¾‚¯Žæ‚èo‚µAAMT_PAYMENT - AMT_INSTALMENT‚Ì•½‹Ï‚ð‚Æ‚Á‚½
 * Å‰‚ÉSK_ID_PREV‚Ågroup by‚µAŽŸ‚ÉSK_ID_CURR‚Ågroup by‚µ‚½
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