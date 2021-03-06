
/*
 * debt_credit_ratio_none
 * SK_ID_CURRでgroup by してAMT_CREDIT_SUM_DEBTの合計をAMT_CREDIT_SUMの合計で割った
 * 登録されている債務の総和/登録されている与信額の総和
 * 付与されている与信額の債務による充足率
 * */
SELECT 
	at2.sk_id_curr 
	,calc.debt_credit_ratio_none
	,CASE calc.debt_credit_ratio_none
	    WHEN 0 THEN 0
	    ELSE 1 
	END as debt_credit_ratio_none_flg
	/*,CASE 
		WHEN calc.debt_credit_ratio_none > 1 THEN 1
		ELSE 0
	END as over_amt_flg*/
FROM application_test at2
LEFT JOIN (
	SELECT 
		app.sk_id_curr 
		,IFNULL(sum(b.amt_credit_sum_debt) / sum(b.amt_credit_sum), '0.0') as debt_credit_ratio_none
	FROM application_test app
	LEFT JOIN bureau b
		ON app.sk_id_curr = b.sk_id_curr
	LEFT JOIN  bureau_balance bb 
		ON b.sk_id_bureau = bb.sk_id_bureau
	GROUP BY app.sk_id_curr
) AS calc
ON at2.sk_id_curr = calc.sk_id_curr
GROUP BY at2.sk_id_curr
;