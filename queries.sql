select * from detectenv.owner;

alter table detectenv.social_media_account
add column probalphan double precision,
add column probbetan double precision,
add column probumalphan double precision,
add column probumbetan double precision;

alter table detectenv.owner
drop column probalphan,
drop column probbetan,
drop column probumalphan,
drop column probumbetan;

ALTER TABLE detectenv.social_media_account ALTER COLUMN id_owner DROP NOT NULL;
ALTER TABLE detectenv.social_media_account ALTER COLUMN screen_name DROP NOT NULL;
ALTER TABLE detectenv.social_media_account ALTER COLUMN date_creation DROP NOT NULL;
ALTER TABLE detectenv.social_media_account ALTER COLUMN blue_badge DROP NOT NULL;

drop function insert_update_social_media_account;

CREATE FUNCTION insert_update_social_media_account(idSocialMediaAccount varchar(30), idSocialMedia int, idOwner int, screenName varchar(30), dateCreation date, blueBadge boolean, prob_AlphaN double precision, prob_BetaN double precision, prob_UmAlphaN double precision, prob_UmBetaN double precision) RETURNS VOID AS $$ 
    DECLARE 
    BEGIN 
		INSERT INTO detectenv.social_media_account(id_account, id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan) values (idSocialMediaAccount, idSocialMedia, idOwner, screenName, dateCreation, blueBadge, prob_AlphaN, prob_BetaN, prob_UmAlphaN, prob_UmBetaN) 
		ON CONFLICT (id_account) DO UPDATE 
			SET probalphan = prob_AlphaN, probbetan = prob_BetaN, probumalphan = prob_UmAlphaN, probumbetan = prob_UmBetaN WHERE hash(id_account) = hash(idSocialMediaAccount);
    END;
    $$ LANGUAGE 'plpgsql'; 

CREATE INDEX idSocialMediaAccount_hash ON detectenv.social_media_account using hash(id_account);
drop index detectenv.idSocialMediaAccount_hash;

CREATE INDEX idnews_original_hash_idx ON detectenv.news using hash(id_news_original);
drop index detectenv.idSocialMediaAccount_hash;

DO $$ BEGIN
    PERFORM insert_update_social_media_account(123, 2, NULL, NULL, NULL, NULL, 0.355, 0.22335233, 0.00122, 0.33325);
END $$;

alter table detectenv.social_media_account
add column id_account varchar(50) not null;

select * from detectenv.social_media_account;
select * from detectenv.social_media;
select * from detectenv.news;
select * from detectenv.post;

alter table detectenv.news alter column id_news type bigint;
alter table detectenv.news alter column datetime_publication drop not null;

alter table detectenv.post
alter column id_post type bigint,
alter column id_social_media_account type bigint,
alter column id_news type bigint,
alter column parent_id_post type bigint,
alter column parent_id_post drop not null,
alter column num_likes drop not null,
alter column num_shares drop not null

alter table detectenv.post drop constraint social_media_account_post_fk;
alter table detectenv.post drop constraint news_post_fk;
alter table detectenv.news alter column id_news_original type varchar(50);

INSERT INTO detectenv.social_media_account(id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan) values (123, NULL, NULL, NULL, NULL, 0.3, 0.22335, 0.001, 0.33325); 
INSERT INTO detectenv.social_media (name_social_media) values ('Twitter');
-- delete from detectenv.post;
-- delete from detectenv.news;
-- ALTER SEQUENCE detectenv.social_media_account_id_social_media_account_seq RESTART WITH 1
-- ALTER SEQUENCE detectenv.post_id_post_seq RESTART WITH 1
-- ALTER SEQUENCE detectenv.news_id_news_seq RESTART WITH 1

ALTER TABLE detectenv.post ADD CONSTRAINT social_media_account_post_fk FOREIGN KEY (id_social_media_account) REFERENCES detectenv.social_media_account (id_social_media_account);

explain analyze select * from detectenv.social_media_account where id_account = '117054157';