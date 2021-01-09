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
        UPDATE detectenv.social_media_account SET probalphan = prob_AlphaN, probbetan = prob_BetaN, probumalphan = prob_UmAlphaN, probumbetan = prob_UmBetaN WHERE id_account = idSocialMediaAccount; 
        IF NOT FOUND THEN
        INSERT INTO detectenv.social_media_account(id_account, id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan) values (idSocialMediaAccount, idSocialMedia, idOwner, screenName, dateCreation, blueBadge, prob_AlphaN, prob_BetaN, prob_UmAlphaN, prob_UmBetaN); 
        END IF; 
    END; 
    $$ LANGUAGE 'plpgsql'; 

CREATE INDEX idSocialMediaAccount_hash ON detectenv.social_media_account using hash(id_account);
drop index detectenv.idSocialMediaAccount_hash;

DO $$ BEGIN
    PERFORM insert_update_social_media_account(123, 2, NULL, NULL, NULL, NULL, 0.355, 0.22335233, 0.00122, 0.33325);
END $$;

alter table detectenv.social_media_account
add column id_account varchar(50) not null;

select * from detectenv.social_media_account;
select * from detectenv.social_media;

INSERT INTO detectenv.social_media_account(id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan) values (123, NULL, NULL, NULL, NULL, 0.3, 0.22335, 0.001, 0.33325); 
INSERT INTO detectenv.social_media (name_social_media) values ('Twitter');
delete from detectenv.social_media_account;

explain analyze select * from detectenv.social_media_account where id_account = '117054157';