--
-- PostgreSQL database dump
--

\restrict wOcCezhEfa5EaU45npyaSp8ITLSotSUQgig8OdnTAdrQxHaACTWmEo4ipW8nUvx

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_keys (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    name character varying(120) NOT NULL,
    key_prefix character varying(32) NOT NULL,
    key_hash character varying(64) NOT NULL,
    status character varying(30) NOT NULL,
    last_used_at timestamp with time zone,
    expires_at timestamp with time zone,
    revoked_at timestamp with time zone,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: custom_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_models (
    owner_id character varying(36) NOT NULL,
    name character varying(160) NOT NULL,
    slug character varying(180) NOT NULL,
    description text,
    category character varying(50) NOT NULL,
    visibility character varying(20) NOT NULL,
    status character varying(30) NOT NULL,
    icon_file_id character varying(36),
    icon_url text,
    improve_from_feedback boolean DEFAULT false NOT NULL,
    readiness_score integer DEFAULT 0 NOT NULL,
    current_version_id character varying(36),
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: data_issues; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_issues (
    dataset_id character varying(36) NOT NULL,
    severity character varying(20) NOT NULL,
    code character varying(80) NOT NULL,
    message text NOT NULL,
    row_number integer,
    field character varying(80),
    details json,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: datasets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.datasets (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    name character varying(160) NOT NULL,
    status character varying(30) NOT NULL,
    readiness_score integer DEFAULT 0 NOT NULL,
    row_count integer DEFAULT 0 NOT NULL,
    valid_count integer DEFAULT 0 NOT NULL,
    invalid_count integer DEFAULT 0 NOT NULL,
    issue_summary json,
    dataset_metadata json,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feedback (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    model_version_id character varying(36),
    request_id character varying(80),
    source character varying(30) NOT NULL,
    input_payload json,
    output_payload json,
    rating character varying(30) NOT NULL,
    comment text,
    status character varying(30) NOT NULL,
    approved_for_training boolean DEFAULT false NOT NULL,
    reviewed_at timestamp with time zone,
    reviewed_by_id character varying(36),
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: model_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.model_versions (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    training_job_id character varying(36),
    version_number integer NOT NULL,
    name character varying(120) NOT NULL,
    status character varying(30) NOT NULL,
    is_active boolean DEFAULT false NOT NULL,
    base_model character varying(160),
    artifact_file_id character varying(36),
    artifact_storage_key text,
    metrics json,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: stored_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stored_files (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36),
    dataset_id character varying(36),
    kind character varying(40) NOT NULL,
    original_filename character varying(255) NOT NULL,
    content_type character varying(120),
    size_bytes integer NOT NULL,
    checksum_sha256 character varying(64) NOT NULL,
    storage_bucket character varying(255) NOT NULL,
    storage_key text NOT NULL,
    public_url text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: training_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.training_jobs (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    dataset_id character varying(36),
    job_type character varying(30) NOT NULL,
    status character varying(30) NOT NULL,
    progress integer DEFAULT 0 NOT NULL,
    current_step character varying(160),
    rq_job_id character varying(120),
    logs json,
    error_message text,
    training_config json,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: usage_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usage_logs (
    owner_id character varying(36) NOT NULL,
    model_id character varying(36) NOT NULL,
    model_version_id character varying(36),
    api_key_id character varying(36),
    request_id character varying(80) NOT NULL,
    endpoint character varying(160) NOT NULL,
    status_code integer NOT NULL,
    latency_ms integer DEFAULT 0 NOT NULL,
    input_units integer DEFAULT 0 NOT NULL,
    output_units integer DEFAULT 0 NOT NULL,
    error_message text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    email character varying(255) NOT NULL,
    full_name character varying(255),
    password_hash character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: custom_models custom_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_models
    ADD CONSTRAINT custom_models_pkey PRIMARY KEY (id);


--
-- Name: data_issues data_issues_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_issues
    ADD CONSTRAINT data_issues_pkey PRIMARY KEY (id);


--
-- Name: datasets datasets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: model_versions model_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_pkey PRIMARY KEY (id);


--
-- Name: stored_files stored_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stored_files
    ADD CONSTRAINT stored_files_pkey PRIMARY KEY (id);


--
-- Name: training_jobs training_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.training_jobs
    ADD CONSTRAINT training_jobs_pkey PRIMARY KEY (id);


--
-- Name: custom_models uq_model_owner_slug; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_models
    ADD CONSTRAINT uq_model_owner_slug UNIQUE (owner_id, slug);


--
-- Name: model_versions uq_model_version_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT uq_model_version_number UNIQUE (model_id, version_number);


--
-- Name: usage_logs usage_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_logs
    ADD CONSTRAINT usage_logs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_api_keys_key_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_api_keys_key_hash ON public.api_keys USING btree (key_hash);


--
-- Name: ix_api_keys_key_prefix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_api_keys_key_prefix ON public.api_keys USING btree (key_prefix);


--
-- Name: ix_api_keys_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_api_keys_model_id ON public.api_keys USING btree (model_id);


--
-- Name: ix_api_keys_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_api_keys_owner_id ON public.api_keys USING btree (owner_id);


--
-- Name: ix_custom_models_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_custom_models_owner_id ON public.custom_models USING btree (owner_id);


--
-- Name: ix_data_issues_dataset_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_data_issues_dataset_id ON public.data_issues USING btree (dataset_id);


--
-- Name: ix_datasets_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_datasets_model_id ON public.datasets USING btree (model_id);


--
-- Name: ix_datasets_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_datasets_owner_id ON public.datasets USING btree (owner_id);


--
-- Name: ix_feedback_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feedback_model_id ON public.feedback USING btree (model_id);


--
-- Name: ix_feedback_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feedback_owner_id ON public.feedback USING btree (owner_id);


--
-- Name: ix_feedback_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feedback_request_id ON public.feedback USING btree (request_id);


--
-- Name: ix_model_versions_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_model_versions_model_id ON public.model_versions USING btree (model_id);


--
-- Name: ix_model_versions_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_model_versions_owner_id ON public.model_versions USING btree (owner_id);


--
-- Name: ix_stored_files_checksum_sha256; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stored_files_checksum_sha256 ON public.stored_files USING btree (checksum_sha256);


--
-- Name: ix_stored_files_dataset_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stored_files_dataset_id ON public.stored_files USING btree (dataset_id);


--
-- Name: ix_stored_files_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stored_files_model_id ON public.stored_files USING btree (model_id);


--
-- Name: ix_stored_files_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stored_files_owner_id ON public.stored_files USING btree (owner_id);


--
-- Name: ix_training_jobs_dataset_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_training_jobs_dataset_id ON public.training_jobs USING btree (dataset_id);


--
-- Name: ix_training_jobs_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_training_jobs_model_id ON public.training_jobs USING btree (model_id);


--
-- Name: ix_training_jobs_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_training_jobs_owner_id ON public.training_jobs USING btree (owner_id);


--
-- Name: ix_training_jobs_rq_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_training_jobs_rq_job_id ON public.training_jobs USING btree (rq_job_id);


--
-- Name: ix_usage_logs_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usage_logs_model_id ON public.usage_logs USING btree (model_id);


--
-- Name: ix_usage_logs_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usage_logs_owner_id ON public.usage_logs USING btree (owner_id);


--
-- Name: ix_usage_logs_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usage_logs_request_id ON public.usage_logs USING btree (request_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: api_keys api_keys_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: api_keys api_keys_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: custom_models custom_models_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_models
    ADD CONSTRAINT custom_models_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: data_issues data_issues_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_issues
    ADD CONSTRAINT data_issues_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: datasets datasets_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: datasets datasets_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_model_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_model_version_id_fkey FOREIGN KEY (model_version_id) REFERENCES public.model_versions(id);


--
-- Name: feedback feedback_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id);


--
-- Name: model_versions model_versions_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: model_versions model_versions_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: model_versions model_versions_training_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_training_job_id_fkey FOREIGN KEY (training_job_id) REFERENCES public.training_jobs(id);


--
-- Name: stored_files stored_files_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stored_files
    ADD CONSTRAINT stored_files_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: stored_files stored_files_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stored_files
    ADD CONSTRAINT stored_files_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: stored_files stored_files_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stored_files
    ADD CONSTRAINT stored_files_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: training_jobs training_jobs_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.training_jobs
    ADD CONSTRAINT training_jobs_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id);


--
-- Name: training_jobs training_jobs_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.training_jobs
    ADD CONSTRAINT training_jobs_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: training_jobs training_jobs_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.training_jobs
    ADD CONSTRAINT training_jobs_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: usage_logs usage_logs_api_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_logs
    ADD CONSTRAINT usage_logs_api_key_id_fkey FOREIGN KEY (api_key_id) REFERENCES public.api_keys(id);


--
-- Name: usage_logs usage_logs_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_logs
    ADD CONSTRAINT usage_logs_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.custom_models(id) ON DELETE CASCADE;


--
-- Name: usage_logs usage_logs_model_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_logs
    ADD CONSTRAINT usage_logs_model_version_id_fkey FOREIGN KEY (model_version_id) REFERENCES public.model_versions(id);


--
-- Name: usage_logs usage_logs_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_logs
    ADD CONSTRAINT usage_logs_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict wOcCezhEfa5EaU45npyaSp8ITLSotSUQgig8OdnTAdrQxHaACTWmEo4ipW8nUvx

