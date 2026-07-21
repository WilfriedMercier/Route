--
-- PostgreSQL database dump
--

\restrict B7h5BQd4ltgtGIMMYWLWs4YPsrdMLV7Ss2Hvb09eV9hW4hPsmjsJ0OcY0KAFXvY

-- Dumped from database version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: hikes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hikes (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    latitude double precision[] NOT NULL,
    longitude double precision[] NOT NULL,
    distances double precision[] NOT NULL,
    elevations double precision[] NOT NULL,
    user_id integer NOT NULL,
    center_lat double precision,
    center_lon double precision
);


--
-- Name: hikes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hikes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hikes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hikes_id_seq OWNED BY public.hikes.id;


--
-- Name: magic_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.magic_links (
    id text CONSTRAINT magic_links_bridge_id_not_null NOT NULL,
    hike_id integer CONSTRAINT magic_links_bridge_hike_id_not_null NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: hikes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hikes ALTER COLUMN id SET DEFAULT nextval('public.hikes_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: hikes hikes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hikes
    ADD CONSTRAINT hikes_pkey PRIMARY KEY (id);


--
-- Name: magic_links magic_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.magic_links
    ADD CONSTRAINT magic_links_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_bridge_hike_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bridge_hike_id ON public.magic_links USING btree (hike_id);


--
-- Name: idx_bridge_magic_link_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bridge_magic_link_id ON public.magic_links USING btree (id);


--
-- Name: idx_hikes_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hikes_user_id ON public.hikes USING btree (user_id);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: magic_links fk_bridge_hike; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.magic_links
    ADD CONSTRAINT fk_bridge_hike FOREIGN KEY (hike_id) REFERENCES public.hikes(id) ON DELETE CASCADE;


--
-- Name: hikes fk_hikes_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hikes
    ADD CONSTRAINT fk_hikes_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict B7h5BQd4ltgtGIMMYWLWs4YPsrdMLV7Ss2Hvb09eV9hW4hPsmjsJ0OcY0KAFXvY

