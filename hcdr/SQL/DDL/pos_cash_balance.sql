use `home-credit-default-risk`;
drop table if exists pos_cash_balance;
create table pos_cash_balance (
sk_id_prev varchar(7)
,sk_id_curr varchar(6)
,months_balance integer
,cnt_instalment integer
,cnt_instalment_future integer
,name_contract_status varchar(128)
,sk_dpd integer
,sk_dpd_def integer
);