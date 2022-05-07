SELECT 
    app.sk_id_curr 
    -- (�S����)�����Z�@�փ��[���̉��ؓ���
    ,IFNULL(max(b2.credit_day_overdue), '0') as hist_max_credit_day_overdue
	,IFNULL(count(b2.credit_day_overdue), '0') as hist_cnt_credit_day_overdue
    ,IFNULL(sum(b2.credit_day_overdue), '0') as hist_sum_credit_day_overdue
    -- (�S����)�N���W�b�g�����񉄒�������
    ,IFNULL(max(b2.cnt_credit_prolong), '0') as hist_max_credit_prolong   -- �ő剄������
    ,IFNULL(count(b2.cnt_credit_prolong), '0') as hist_cnt_credit_prolong -- �o�^��
	,IFNULL(sum(b2.cnt_credit_prolong), '0') as hist_sum_credit_prolong   -- �o�^����Ă���ő剄�������̍��v
	-- ����܂ł̍ő剄�؋��z
	,IFNULL(max(b2.amt_credit_max_overdue), '0') as hist_max_amt_credit_max_overdue   -- �ő剄�؋��z 
	,IFNULL(count(b2.amt_credit_max_overdue), '0') as hist_cnt_amt_credit_max_overdue -- ���؋��z�L�^��
	,IFNULL(sum(b2.amt_credit_max_overdue), '0') as hist_sum_amt_credit_max_overdue   -- �ߋ��ɓo�^���ꂽ���؋��z�̍��v
FROM application_test app
LEFT JOIN bureau b2
	ON app.sk_id_curr = b2.sk_id_curr
LEFT JOIN  bureau_balance bb2 
	ON b2.sk_id_bureau = bb2.sk_id_bureau
	GROUP BY app.sk_id_curr;