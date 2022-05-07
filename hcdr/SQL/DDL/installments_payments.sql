use `home-credit-default-risk`;
drop table if exists installments_payments;
create table installments_payments (
sk_id_prev varchar(7)
,sk_id_curr varchar(6)
,num_instalment_version integer
,num_instalment_number integer
,days_instalment integer
,days_entry_payment integer
,amt_instalment double
,amt_payment double
);