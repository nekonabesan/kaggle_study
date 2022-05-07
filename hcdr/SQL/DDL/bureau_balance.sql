use `home-credit-default-risk`;
drop table if exists bureau_balance; 
create table bureau_balance (
sk_id_bureau varchar(7) 
,months_balance integer
,status varchar(1)
);