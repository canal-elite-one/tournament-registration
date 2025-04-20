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

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    category_id character(1) NOT NULL,
    alternate_name character varying(64),
    color character varying(7),
    min_points integer DEFAULT 0 NOT NULL,
    max_points integer DEFAULT 4000 NOT NULL,
    start_time timestamp without time zone NOT NULL,
    women_only boolean DEFAULT false NOT NULL,
    base_registration_fee integer NOT NULL,
    late_registration_fee integer NOT NULL,
    reward_first integer NOT NULL,
    reward_second integer NOT NULL,
    reward_semi integer NOT NULL,
    reward_quarter integer,
    max_players integer NOT NULL,
    overbooking_percentage integer DEFAULT 0 NOT NULL
);


--
-- Name: entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entries (
    category_id character(1) NOT NULL,
    licence_no character varying(20) NOT NULL,
    color character varying(7),
    registration_time timestamp without time zone DEFAULT now() NOT NULL,
    marked_as_present boolean,
    marked_as_paid boolean DEFAULT false NOT NULL
);


--
-- Name: players; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players (
    licence_no character varying(20) NOT NULL,
    bib_no integer,
    first_name character varying(64) NOT NULL,
    last_name character varying(64) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(15) NOT NULL,
    gender character(1) NOT NULL,
    nb_points integer NOT NULL,
    club character varying(255) NOT NULL,
    total_actual_paid integer DEFAULT 0 NOT NULL
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: entries entries_color_licence_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entries
    ADD CONSTRAINT entries_color_licence_no_key UNIQUE (color, licence_no);


--
-- Name: entries entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entries
    ADD CONSTRAINT entries_pkey PRIMARY KEY (category_id, licence_no);


--
-- Name: players players_bib_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_bib_no_key UNIQUE (bib_no);


--
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (licence_no);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: entries entries_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entries
    ADD CONSTRAINT entries_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE RESTRICT;


--
-- Name: entries entries_licence_no_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entries
    ADD CONSTRAINT entries_licence_no_fkey FOREIGN KEY (licence_no) REFERENCES public.players(licence_no) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20231124152614');
