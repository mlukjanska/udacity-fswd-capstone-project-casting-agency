DROP DATABASE IF EXISTS casting_agency;
DROP USER IF EXISTS db_admin;
CREATE DATABASE casting_agency;
CREATE USER db_admin WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE casting_agency TO db_admin;
ALTER USER db_admin CREATEDB;
ALTER USER db_admin WITH SUPERUSER;
\c casting_agency db_admin

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.3
-- Dumped by pg_dump version 11.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- PostgreSQL database dump complete
--