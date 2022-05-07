SELECT 
    app.sk_id_curr 
    -- (‘SŠúŠÔ)‘¼‹à—Z‹@ŠÖƒ[ƒ“‚Ì‰„‘Ø“ú”
    ,IFNULL(max(b2.credit_day_overdue), '0') as hist_max_credit_day_overdue
	,IFNULL(count(b2.credit_day_overdue), '0') as hist_cnt_credit_day_overdue
    ,IFNULL(sum(b2.credit_day_overdue), '0') as hist_sum_credit_day_overdue
    -- (‘SŠúŠÔ)ƒNƒŒƒWƒbƒg‚ğ‰½‰ñ‰„’·‚µ‚½‚©
    ,IFNULL(max(b2.cnt_credit_prolong), '0') as hist_max_credit_prolong   -- Å‘å‰„’·“ú”
    ,IFNULL(count(b2.cnt_credit_prolong), '0') as hist_cnt_credit_prolong -- “o˜^‰ñ”
	,IFNULL(sum(b2.cnt_credit_prolong), '0') as hist_sum_credit_prolong   -- “o˜^‚³‚ê‚Ä‚¢‚éÅ‘å‰„’·“ú”‚Ì‡Œv
	-- ‚±‚ê‚Ü‚Å‚ÌÅ‘å‰„‘Ø‹àŠz
	,IFNULL(max(b2.amt_credit_max_overdue), '0') as hist_max_amt_credit_max_overdue   -- Å‘å‰„‘Ø‹àŠz 
	,IFNULL(count(b2.amt_credit_max_overdue), '0') as hist_cnt_amt_credit_max_overdue -- ‰„‘Ø‹àŠz‹L˜^‰ñ”
	,IFNULL(sum(b2.amt_credit_max_overdue), '0') as hist_sum_amt_credit_max_overdue   -- ‰ß‹‚É“o˜^‚³‚ê‚½‰„‘Ø‹àŠz‚Ì‡Œv
FROM application_test app
LEFT JOIN bureau b2
	ON app.sk_id_curr = b2.sk_id_curr
LEFT JOIN  bureau_balance bb2 
	ON b2.sk_id_bureau = bb2.sk_id_bureau
	GROUP BY app.sk_id_curr;