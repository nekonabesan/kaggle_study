use `home-credit-default-risk`;
drop table if exists bureau;
create table bureau (
sk_id_curr varchar(6)
,sk_id_bureau varchar(7)
,credit_active varchar(128)
,credit_currency  varchar(128)
,days_credit  integer
,credit_day_overdue integer
,days_credit_enddate integer
,days_enddate_fact integer
,amt_credit_max_overdue double
,cnt_credit_prolong double
,amt_credit_sum double
,amt_credit_sum_debt double
,amt_credit_sum_limit double
,amt_credit_sum_overdue double
,credit_type varchar(128)
,days_credit_update integer
)
