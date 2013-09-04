--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cpe; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE cpe (
    id numeric(8,0) NOT NULL,
    cpe character varying(170) NOT NULL
);


ALTER TABLE public.cpe OWNER TO prey;

--
-- Name: seq_hostname_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_hostname_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_hostname_id OWNER TO prey;

--
-- Name: hostnames; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE hostnames (
    id numeric(8,0) DEFAULT nextval('seq_hostname_id'::regclass) NOT NULL,
    host_id numeric(8,0) NOT NULL,
    name character varying(75) NOT NULL,
    type character varying(8) NOT NULL
);


ALTER TABLE public.hostnames OWNER TO prey;

--
-- Name: hosts; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE hosts (
    id numeric(8,0) NOT NULL,
    address character varying(45) NOT NULL,
    addrtype character(2) NOT NULL,
    state character(1) NOT NULL,
    "time" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.hosts OWNER TO prey;

--
-- Name: COLUMN hosts.addrtype; Type: COMMENT; Schema: public; Owner: prey
--

COMMENT ON COLUMN hosts.addrtype IS '''4'' - IPv4, ''6'' - IPv6';


--
-- Name: COLUMN hosts.state; Type: COMMENT; Schema: public; Owner: prey
--

COMMENT ON COLUMN hosts.state IS '''U'' - up, ''D'' - down';


--
-- Name: http_headers; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE http_headers (
    page_id numeric(8,0) NOT NULL,
    name character varying(45) NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.http_headers OWNER TO prey;

--
-- Name: os; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE os (
    id numeric(8,0) NOT NULL,
    host_id numeric(8,0) NOT NULL
);


ALTER TABLE public.os OWNER TO prey;

--
-- Name: os_osclass; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE os_osclass (
    id numeric(8,0) NOT NULL,
    osmatch_id numeric(8,0) NOT NULL,
    vendor character varying(256) NOT NULL,
    accuracy numeric(3,0) NOT NULL,
    osfamily character varying(128) NOT NULL,
    osgen character varying(45),
    type character varying(45)
);


ALTER TABLE public.os_osclass OWNER TO prey;

--
-- Name: os_osclass_cpe; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE os_osclass_cpe (
    osclass_id numeric(8,0) NOT NULL,
    cpe_id numeric(8,0) NOT NULL
);


ALTER TABLE public.os_osclass_cpe OWNER TO prey;

--
-- Name: os_osmatch; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE os_osmatch (
    id numeric(8,0) NOT NULL,
    os_id numeric(8,0) NOT NULL,
    name character varying(128) NOT NULL,
    accuracy numeric(3,0) NOT NULL,
    line numeric(10,0) NOT NULL
);


ALTER TABLE public.os_osmatch OWNER TO prey;

--
-- Name: os_used_ports; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE os_used_ports (
    os_id numeric(8,0) NOT NULL,
    state character(1) NOT NULL,
    proto character(4) NOT NULL,
    portid numeric(5,0) NOT NULL
);


ALTER TABLE public.os_used_ports OWNER TO prey;

--
-- Name: ports; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE ports (
    port numeric(5,0) NOT NULL,
    host_id numeric(8,0) NOT NULL,
    protocol character(3) NOT NULL,
    state character(1) NOT NULL,
    reason character varying(32) NOT NULL
);


ALTER TABLE public.ports OWNER TO prey;

--
-- Name: COLUMN ports.state; Type: COMMENT; Schema: public; Owner: prey
--

COMMENT ON COLUMN ports.state IS '''O'' - open, ''C'' - closed';


--
-- Name: seq_script_result_element_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_script_result_element_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_script_result_element_id OWNER TO prey;

--
-- Name: script_result_elements; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE script_result_elements (
    id numeric(8,0) DEFAULT nextval('seq_script_result_element_id'::regclass) NOT NULL,
    script_result_id numeric(8,0) NOT NULL,
    key character varying(32) NOT NULL,
    text text
);


ALTER TABLE public.script_result_elements OWNER TO prey;

--
-- Name: seq_script_result_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_script_result_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_script_result_id OWNER TO prey;

--
-- Name: script_results; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE script_results (
    id numeric(8,0) DEFAULT nextval('seq_script_result_id'::regclass) NOT NULL,
    host_id numeric(8,0) NOT NULL,
    port numeric(5,0) NOT NULL,
    name character varying(45) NOT NULL,
    output text
);


ALTER TABLE public.script_results OWNER TO prey;

--
-- Name: seq_cpe_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_cpe_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_cpe_id OWNER TO prey;

--
-- Name: seq_host_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_host_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_host_id OWNER TO prey;

--
-- Name: seq_os_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_os_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_os_id OWNER TO prey;

--
-- Name: seq_osclass_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_osclass_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_osclass_id OWNER TO prey;

--
-- Name: seq_osmatch_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_osmatch_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_osmatch_id OWNER TO prey;

--
-- Name: seq_page_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_page_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_page_id OWNER TO prey;

--
-- Name: seq_url_id; Type: SEQUENCE; Schema: public; Owner: prey
--

CREATE SEQUENCE seq_url_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_url_id OWNER TO prey;

--
-- Name: service_cpe; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE service_cpe (
    host_id numeric(8,0) NOT NULL,
    port numeric(5,0) NOT NULL,
    cpe_id numeric(8,0) NOT NULL
);


ALTER TABLE public.service_cpe OWNER TO prey;

--
-- Name: services; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE services (
    host_id numeric(8,0) NOT NULL,
    port numeric(5,0) NOT NULL,
    name character varying(32) NOT NULL,
    product character varying(128),
    method character(2) NOT NULL,
    version character varying(64),
    extrainfo character varying(128),
    ostype character varying(64),
    conf numeric(4,0) NOT NULL,
    hostname character varying(70),
    tunnel character(1),
    proto character(1),
    rpcnum numeric(8,0),
    lowver numeric(8,0),
    highver numeric(8,0),
    devicetype character varying(32),
    servicefp text
);


ALTER TABLE public.services OWNER TO prey;

--
-- Name: COLUMN services.tunnel; Type: COMMENT; Schema: public; Owner: prey
--

COMMENT ON COLUMN services.tunnel IS '''S'' - ssh';


--
-- Name: COLUMN services.proto; Type: COMMENT; Schema: public; Owner: prey
--

COMMENT ON COLUMN services.proto IS '''R'' - rpc';


--
-- Name: url_queries; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE url_queries (
    url_id numeric(8,0) NOT NULL,
    key character varying(45) NOT NULL,
    value character varying(128),
    order_num numeric(3,0) NOT NULL
);


ALTER TABLE public.url_queries OWNER TO prey;

--
-- Name: urls; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE urls (
    id numeric(8,0) NOT NULL,
    scheme character varying(8) NOT NULL,
    username character varying(45),
    password character varying(45),
    location character varying(256) NOT NULL,
    port numeric(5,0),
    path character varying(512) DEFAULT '/'::character varying NOT NULL,
    redirect_url_id numeric(8,0)
);


ALTER TABLE public.urls OWNER TO prey;

--
-- Name: url_view; Type: VIEW; Schema: public; Owner: prey
--

CREATE VIEW url_view AS
    SELECT urls.id, (((((((urls.scheme)::text || '://'::text) || CASE WHEN ((urls.username IS NULL) AND (urls.password IS NULL)) THEN ''::text ELSE (((COALESCE(urls.username, ''::character varying))::text || COALESCE((':'::text || (urls.password)::text), ''::text)) || '@'::text) END) || (urls.location)::text) || CASE WHEN (urls.port IS NULL) THEN ''::text ELSE (':'::text || urls.port) END) || (urls.path)::text) || CASE WHEN ((SELECT count(*) AS count FROM url_queries WHERE (urls.id = url_queries.url_id)) > 0) THEN ('?'::text || (SELECT array_to_string(array_agg((((url_queries.key)::text || '='::text) || (url_queries.value)::text)), '&'::text) AS array_to_string FROM url_queries WHERE (url_queries.url_id = urls.id))) ELSE ''::text END) AS url FROM urls GROUP BY urls.id, urls.scheme, urls.username, urls.password, urls.location, urls.port, urls.path;


ALTER TABLE public.url_view OWNER TO prey;

--
-- Name: urls_resolved_to_hosts; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE urls_resolved_to_hosts (
    url_id numeric(8,0) NOT NULL,
    host_id numeric(8,0) NOT NULL
);


ALTER TABLE public.urls_resolved_to_hosts OWNER TO prey;

--
-- Name: www_page_additional_info; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE www_page_additional_info (
    page_id numeric(8,0) NOT NULL,
    class character varying(45) NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.www_page_additional_info OWNER TO prey;

--
-- Name: www_page_error_extras; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE www_page_error_extras (
    page_id numeric(8,0) NOT NULL,
    url_id numeric(8,0) NOT NULL,
    error_message text NOT NULL
);


ALTER TABLE public.www_page_error_extras OWNER TO prey;

--
-- Name: www_page_fetch_info; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE www_page_fetch_info (
    page_id numeric(8,0) NOT NULL,
    url_id numeric(8,0) NOT NULL,
    version character varying(10) NOT NULL,
    status_code numeric(3,0) NOT NULL,
    message character varying(45) NOT NULL
);


ALTER TABLE public.www_page_fetch_info OWNER TO prey;

--
-- Name: www_page_located_at_urls; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE www_page_located_at_urls (
    page_id numeric(8,0) NOT NULL,
    url_id numeric(8,0) NOT NULL,
    fetched boolean,
    "time" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.www_page_located_at_urls OWNER TO prey;

--
-- Name: www_pages; Type: TABLE; Schema: public; Owner: prey; Tablespace: 
--

CREATE TABLE www_pages (
    id numeric(8,0) NOT NULL,
    title text
);


ALTER TABLE public.www_pages OWNER TO prey;

--
-- Name: cpe_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY cpe
    ADD CONSTRAINT cpe_pkey PRIMARY KEY (id);


--
-- Name: hostnames_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY hostnames
    ADD CONSTRAINT hostnames_pkey PRIMARY KEY (id);


--
-- Name: hosts_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY hosts
    ADD CONSTRAINT hosts_pkey PRIMARY KEY (id);


--
-- Name: os_osclass_cpe_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY os_osclass_cpe
    ADD CONSTRAINT os_osclass_cpe_pkey PRIMARY KEY (osclass_id, cpe_id);


--
-- Name: os_osclass_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY os_osclass
    ADD CONSTRAINT os_osclass_pkey PRIMARY KEY (id);


--
-- Name: os_osmatch_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY os_osmatch
    ADD CONSTRAINT os_osmatch_pkey PRIMARY KEY (id);


--
-- Name: os_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_pkey PRIMARY KEY (id);


--
-- Name: ports_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY ports
    ADD CONSTRAINT ports_pkey PRIMARY KEY (port, host_id);


--
-- Name: script_result_elements_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY script_result_elements
    ADD CONSTRAINT script_result_elements_pkey PRIMARY KEY (id);


--
-- Name: script_results_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY script_results
    ADD CONSTRAINT script_results_pkey PRIMARY KEY (id);


--
-- Name: service_cpe_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY service_cpe
    ADD CONSTRAINT service_cpe_pkey PRIMARY KEY (host_id, port, cpe_id);


--
-- Name: services_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY services
    ADD CONSTRAINT services_pkey PRIMARY KEY (host_id, port);


--
-- Name: urls_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_pkey PRIMARY KEY (id);


--
-- Name: urls_resolved_to_hosts_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY urls_resolved_to_hosts
    ADD CONSTRAINT urls_resolved_to_hosts_pkey PRIMARY KEY (url_id, host_id);


--
-- Name: www_page_error_extras_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY www_page_error_extras
    ADD CONSTRAINT www_page_error_extras_pkey PRIMARY KEY (page_id, url_id);


--
-- Name: www_page_fetch_info_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY www_page_fetch_info
    ADD CONSTRAINT www_page_fetch_info_pkey PRIMARY KEY (page_id, url_id);


--
-- Name: www_page_located_at_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY www_page_located_at_urls
    ADD CONSTRAINT www_page_located_at_urls_pkey PRIMARY KEY (page_id, url_id);


--
-- Name: www_pages_pkey; Type: CONSTRAINT; Schema: public; Owner: prey; Tablespace: 
--

ALTER TABLE ONLY www_pages
    ADD CONSTRAINT www_pages_pkey PRIMARY KEY (id);


--
-- Name: hostnames_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY hostnames
    ADD CONSTRAINT hostnames_host_id_fkey FOREIGN KEY (host_id) REFERENCES hosts(id);


--
-- Name: http_headers_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY http_headers
    ADD CONSTRAINT http_headers_page_id_fkey FOREIGN KEY (page_id) REFERENCES www_pages(id);


--
-- Name: os_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_host_id_fkey FOREIGN KEY (host_id) REFERENCES hosts(id);


--
-- Name: os_osclass_cpe_cpe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os_osclass_cpe
    ADD CONSTRAINT os_osclass_cpe_cpe_id_fkey FOREIGN KEY (cpe_id) REFERENCES cpe(id);


--
-- Name: os_osclass_cpe_osclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os_osclass_cpe
    ADD CONSTRAINT os_osclass_cpe_osclass_id_fkey FOREIGN KEY (osclass_id) REFERENCES os_osclass(id);


--
-- Name: os_osclass_os_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os_osclass
    ADD CONSTRAINT os_osclass_os_match_id_fkey FOREIGN KEY (osmatch_id) REFERENCES os_osmatch(id);


--
-- Name: os_osmatch_os_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os_osmatch
    ADD CONSTRAINT os_osmatch_os_id_fkey FOREIGN KEY (os_id) REFERENCES os(id);


--
-- Name: os_used_ports_os_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY os_used_ports
    ADD CONSTRAINT os_used_ports_os_id_fkey FOREIGN KEY (os_id) REFERENCES os(id);


--
-- Name: ports_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY ports
    ADD CONSTRAINT ports_host_id_fkey FOREIGN KEY (host_id) REFERENCES hosts(id);


--
-- Name: script_result_elements_script_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY script_result_elements
    ADD CONSTRAINT script_result_elements_script_result_id_fkey FOREIGN KEY (script_result_id) REFERENCES script_results(id);


--
-- Name: script_results_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY script_results
    ADD CONSTRAINT script_results_host_id_fkey FOREIGN KEY (host_id, port) REFERENCES ports(host_id, port);


--
-- Name: service_cpe_cpe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY service_cpe
    ADD CONSTRAINT service_cpe_cpe_id_fkey FOREIGN KEY (cpe_id) REFERENCES cpe(id);


--
-- Name: service_cpe_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY service_cpe
    ADD CONSTRAINT service_cpe_host_id_fkey FOREIGN KEY (host_id, port) REFERENCES services(host_id, port);


--
-- Name: services_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY services
    ADD CONSTRAINT services_host_id_fkey FOREIGN KEY (host_id, port) REFERENCES ports(host_id, port);


--
-- Name: url_queries_url_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY url_queries
    ADD CONSTRAINT url_queries_url_id_fkey FOREIGN KEY (url_id) REFERENCES urls(id);


--
-- Name: urls_redirect_url_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_redirect_url_id_fkey FOREIGN KEY (redirect_url_id) REFERENCES urls(id);


--
-- Name: urls_resolved_to_hosts_host_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY urls_resolved_to_hosts
    ADD CONSTRAINT urls_resolved_to_hosts_host_id_fkey FOREIGN KEY (host_id) REFERENCES hosts(id);


--
-- Name: urls_resolved_to_hosts_url_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY urls_resolved_to_hosts
    ADD CONSTRAINT urls_resolved_to_hosts_url_id_fkey FOREIGN KEY (url_id) REFERENCES urls(id);


--
-- Name: www_page_additional_info_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY www_page_additional_info
    ADD CONSTRAINT www_page_additional_info_page_id_fkey FOREIGN KEY (page_id) REFERENCES www_pages(id);


--
-- Name: www_page_error_extras_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY www_page_error_extras
    ADD CONSTRAINT www_page_error_extras_page_id_fkey FOREIGN KEY (page_id, url_id) REFERENCES www_page_located_at_urls(page_id, url_id);


--
-- Name: www_page_fetch_info_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY www_page_fetch_info
    ADD CONSTRAINT www_page_fetch_info_page_id_fkey FOREIGN KEY (page_id, url_id) REFERENCES www_page_located_at_urls(page_id, url_id);


--
-- Name: www_page_located_at_urls_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY www_page_located_at_urls
    ADD CONSTRAINT www_page_located_at_urls_page_id_fkey FOREIGN KEY (page_id) REFERENCES www_pages(id);


--
-- Name: www_page_located_at_urls_url_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: prey
--

ALTER TABLE ONLY www_page_located_at_urls
    ADD CONSTRAINT www_page_located_at_urls_url_id_fkey FOREIGN KEY (url_id) REFERENCES urls(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

