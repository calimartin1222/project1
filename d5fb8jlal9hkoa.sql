-- Adminer 4.6.3-dev PostgreSQL dump

\connect "d5fb8jlal9hkoa";

DROP TABLE IF EXISTS "checkins";
DROP SEQUENCE IF EXISTS checkins_id_seq;
CREATE SEQUENCE checkins_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."checkins" (
    "id" integer DEFAULT nextval('checkins_id_seq') NOT NULL,
    "location" character varying NOT NULL,
    "username" character varying NOT NULL,
    "comment" character varying,
    CONSTRAINT "checkins_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "locations";
DROP SEQUENCE IF EXISTS locations_id_seq;
CREATE SEQUENCE locations_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."locations" (
    "id" integer DEFAULT nextval('locations_id_seq') NOT NULL,
    "zip" character(5) NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "lat" character varying NOT NULL,
    "long" character varying NOT NULL,
    "pop" character varying NOT NULL,
    CONSTRAINT "locations_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "userinfo";
DROP SEQUENCE IF EXISTS userinfo_id_seq;
CREATE SEQUENCE userinfo_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."userinfo" (
    "id" integer DEFAULT nextval('userinfo_id_seq') NOT NULL,
    "first" character varying NOT NULL,
    "uname" character varying NOT NULL,
    "pword" character varying NOT NULL,
    CONSTRAINT "userinfo_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


-- 2018-07-12 21:02:59.704561+00
