/**
 * DAYS_CREDIT_mean
 * bureau�ɂ���CREDIT_DAYS��SK_ID_CURR��groupby��������
 * */
SELECT 
    at2.sk_id_curr 
    ,IFNULL(avg(b.days_credit), '0') as avg_days_credit
	,IFNULL(avg(b.days_credit_enddate), '0') as avg_days_credit_enddate
	,IFNULL(avg(b.days_enddate_fact), '0') as avg_days_enddate_fact
FROM application_train at2 
LEFT JOIN bureau b
	ON at2.sk_id_curr = b.sk_id_curr
GROUP BY at2.sk_id_curr;