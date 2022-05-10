--
-- annuity_to_max_installment_ratio
-- AMT_ANNUITY / (installments_paymentsをSK_ID_CURRでgroup byしたのち、最大のinstallment)
-- ローン支払い額 / 実際の支払日  - 申し込み日(基本マイナス)
-- 
SELECT 
ip2.sk_id_curr
,at3.amt_annuity/max(ip2.days_instalment) as revo_annuity_to_max_installment_ratio
-- FROM application_train at3
FROM application_test at3
INNER JOIN previous_application pa2 
ON at3.sk_id_curr = pa2.sk_id_curr
INNER JOIN credit_card_balance ccb2
ON pa2.sk_id_prev = ccb2.sk_id_prev 
AND pa2.sk_id_curr = ccb2.sk_id_curr
INNER JOIN installments_payments ip2 
ON ccb2.sk_id_prev = ip2.sk_id_prev 
AND ccb2.sk_id_curr = ip2.sk_id_curr
WHERE 
-- (pa2.name_contract_type = "Cash loans" OR pa.name_contract_type = "Consumer loans")
-- at3.name_contract_type = "Cash loans"
-- at3.name_contract_type = "Revolving loans"
-- pa2.name_contract_type = "Revolving loans"
pa2.name_contract_type = "Revolving loans"
AND pa2.flag_last_appl_per_contract = "Y"
AND ccb2.months_balance = -1
AND ip2.num_instalment_version = 0
GROUP BY ip2.sk_id_curr
ORDER BY ip2.sk_id_curr,ip2.sk_id_prev 
;