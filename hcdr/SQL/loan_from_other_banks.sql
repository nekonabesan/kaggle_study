use `home-credit-default-risk`;
/**
 * Loan From other banks
 * */
SELECT 
at2.sk_id_curr
,b.sk_id_bureau
-- ,at2.target 
/*,at2.name_contract_type
,at2.code_gender
,at2.flag_own_car
,at2.flag_own_realty
,at2.cnt_children
,at2.name_type_suite
,at2.name_income_type
,at2.name_education_type
,at2.name_family_status
,at2.name_housing_type
,at2.region_population_relative
,at2.days_birth
,at2.days_employed
,at2.own_car_age
,at2.occupation_type
,at2.cnt_fam_members
,at2.region_rating_client
,at2.region_rating_client_w_city
,at2.organization_type
,at2.ext_source_1
,at2.ext_source_2
,at2.ext_source_3*/
/**/
-- ,b.credit_active 
-- ,b.credit_currency 
,IFNULL(max(b.credit_day_overdue), '0') as max_credit_day_overdue   -- (�\���݌�)�\�����ݎ��_�ł̑����Z�@�փ��[���̉��ؓ���
,IFNULL(max(b.days_credit_enddate), '0') as max_days_credit_enddate -- �\�����ݎ��_�ł̑����Z�@�փ��[���̎c��̓���
,IFNULL(min(b.days_enddate_fact), '0') as min_days_enddate_fact     -- �\�����ݎ��_�ł̑����Z�@�փ��[���������I����Ă���ꍇ�̕����I����Ă���̓���
,IFNULL(max(b.amt_credit_max_overdue), '0') as max_amt_credit_max_overdue -- (�\���݌�)����܂ł̍ő剄�؋��z
,IFNULL(count(b.cnt_credit_prolong), '0') as cnt_credit_prolong           -- (�\���݌�)�N���W�b�g�����񉄒�������(����)
,IFNULL(max(b.cnt_credit_prolong), '0') as max_credit_prolong             -- (�\���݌�)�N���W�b�g�����񉄒�������(�ő�)
,IFNULL(sum(b.amt_credit_sum), '0') as sum_amt_credit_sum                 -- (�\���݌�)�M�p���@�֓o�^����Ă���^�M�z�̑��a
,IFNULL(sum(b.amt_credit_sum_debt), '0') as sum_amt_credit_sum_debt       -- (�\���݌�)�M�p���@�ւɓo�^����Ă����
,IFNULL(sum(b.amt_credit_sum_limit), '0') as sum_amt_credit_sum_limit     -- (�\���݌�)�M�p���@�ւɓo�^����Ă���N���W�b�g�J�[�h�̌��x�z
,IFNULL(sum(b.amt_credit_sum_overdue), '0') as sum_amt_credit_sum_overdue -- (�\���݌�)�M�p���@�ւɓo�^����Ă���N���W�b�g�J�[�h�̎c��(�g�p�z)
,IFNULL(b.credit_type, 'NaN') as credit_type
,IFNULL(max(b.days_credit_update), '0') as max_days_credit_update         -- �\�����ݓ�����A�M�p���@�ւɍŌ�ɏ�񂪓o�^���ꂽ���܂ł̓���
,IFNULL(sum(b.amt_annuity), '0.0') as sum_amt_annuity                     -- �o�^����Ă��郍�[���x�����z
-- ,bb.months_balance 
-- ,bb.status
/*,hist.max_credit_day_overdue
,hist.cnt_credit_day_overdue
,hist.sum_credit_day_overdue
,hist.max_credit_prolong
,hist.cnt_credit_prolong
,hist.sum_credit_day_overdue
,hist.max_amt_credit_max_overdue
,hist.cnt_amt_credit_max_overdue
,hist.sum_amt_credit_max_overdue*/
FROM application_train at2 
-- FROM application_test at2
LEFT JOIN bureau b
ON at2.sk_id_curr = b.sk_id_curr
LEFT JOIN  bureau_balance bb 
ON b.sk_id_bureau = bb.sk_id_bureau
/*LEFT JOIN (
	SELECT 
	    app.sk_id_curr 
	    -- (�S����)�����Z�@�փ��[���̉��ؓ���
	    ,IFNULL(max(b2.credit_day_overdue), '0') as max_credit_day_overdue
		,IFNULL(count(b2.credit_day_overdue), '0') as cnt_credit_day_overdue
	    ,IFNULL(sum(b2.credit_day_overdue), '0') as sum_credit_day_overdue
	    -- (�S����)�N���W�b�g�����񉄒�������
	    ,IFNULL(max(b2.cnt_credit_prolong), '0') as max_credit_prolong   -- �ő剄������
	    ,IFNULL(count(b2.cnt_credit_prolong), '0') as cnt_credit_prolong -- �o�^��
		,IFNULL(sum(b2.cnt_credit_prolong), '0') as sum_credit_prolong   -- �o�^����Ă���ő剄�������̍��v
		-- ����܂ł̍ő剄�؋��z
		,IFNULL(max(b2.amt_credit_max_overdue), '0') as max_amt_credit_max_overdue   -- �ő剄�؋��z 
		,IFNULL(count(b2.amt_credit_max_overdue), '0') as cnt_amt_credit_max_overdue -- ���؋��z�L�^��
		,IFNULL(sum(b2.amt_credit_max_overdue), '0') as sum_amt_credit_max_overdue   -- �ߋ��ɓo�^���ꂽ���؋��z�̍��v
	FROM application_trein app
	LEFT JOIN bureau b2
		ON app.sk_id_curr = b2.sk_id_curr
	LEFT JOIN  bureau_balance bb2 
		ON b2.sk_id_bureau = bb2.sk_id_bureau
	GROUP BY app.sk_id_curr
) as hist
ON at2.sk_id_curr = hist.sk_id_curr*/
-- ================================================================= --
-- Consumer credit
-- Credit card
-- Other, Car loan, Microlone ......
-- ================================================================= --
WHERE bb.months_balance = 0
-- AND b.credit_type = "Consumer credit"   -- �N���W�b�g�J�[�h(���[���_��?)�̎��
-- AND ABS(bb.months_balance) <= 12          -- ���[���\�����ݓ�����̉������O���̕ϐ�(-1�ł���Β��ߌ����Ӗ�����)
-- AND b.days_credit_update >= -180 

GROUP BY at2.sk_id_curr
ORDER BY at2.sk_id_curr, b.sk_id_bureau, b.days_credit_update  
;