use `home-credit-default-risk`;
drop table if exists credit_card_balance;
create table credit_card_balance (
sk_id_prev varchar(7)
,sk_id_curr varchar(6)
,months_balance	integer
,amt_balance double
,amt_credit_limit_actual integer
,amt_drawings_atm_current double
,amt_drawings_current double
,amt_drawings_other_current double
,amt_drawings_pos_current double
,amt_inst_min_regularity double
,amt_payment_current double
,amt_payment_total_current double
,amt_receivable_principal double
,amt_recivable double
,amt_total_receivable double
,cnt_drawings_atm_current integer
,cnt_drawings_current integer
,cnt_drawings_other_current integer
,cnt_drawings_pos_current integer
,cnt_instalment_mature_cum integer
,name_contract_status varchar(128)
,sk_dpd integer
,sk_dpd_def integer
);