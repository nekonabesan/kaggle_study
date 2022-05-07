
/*
 * debt_credit_ratio_none
 * SK_ID_CURR‚Ågroup by ‚µ‚ÄAMT_CREDIT_SUM_DEBT‚Ì‡Œv‚ðAMT_CREDIT_SUM‚Ì‡Œv‚ÅŠ„‚Á‚½
 * “o˜^‚³‚ê‚Ä‚¢‚éÂ–±‚Ì‘˜a/“o˜^‚³‚ê‚Ä‚¢‚é—^MŠz‚Ì‘˜a
 * •t—^‚³‚ê‚Ä‚¢‚é—^MŠz‚ÌÂ–±‚É‚æ‚é[‘«—¦
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