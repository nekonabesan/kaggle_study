/**
 * Loan From Home Credit(Cash loans)
 * installment_payment_ratio_1000_mean_mean
 * nstallment paymentsの中でDAYS_INSTALLMENT>-1000のものだけ取り出し、AMT_pa4YMENT - AMT_INSTALMENTの平均をとった
 * 最初にSK_ID_PREVでgroup byし、次にSK_ID_CURRでgroup byした
 * */
SELECT 
at4.sk_id_curr
-- ,pa4.sk_id_prev
,avg(ip4.amt_payment - ip4.amt_instalment) as revo_installment_payment_ratio_1000_mean_mean
-- FROM application_train at4
FROM application_test at4
INNER JOIN previous_application pa4 
ON at4.sk_id_curr = pa4.sk_id_curr
INNER JOIN installments_payments ip4 
ON pa4.sk_id_curr = ip4.sk_id_curr 
AND pa4.sk_id_prev = ip4.sk_id_prev
WHERE 
-- (pa4.name_contract_type = "Cash loans" OR pa4.name_contract_type = "Consumer loans")
pa4.name_contract_type = "Revolving loans"
AND ip4.days_instalment > -1000
GROUP BY at4.sk_id_curr