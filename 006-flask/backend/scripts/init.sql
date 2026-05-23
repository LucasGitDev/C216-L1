-- Schema for the professores CRUD service.
-- Mounted at /docker-entrypoint-initdb.d/init.sql so the postgres image runs it
-- on first boot.

CREATE TABLE IF NOT EXISTS professores (
    id                   SERIAL      PRIMARY KEY,
    nome                 VARCHAR(100) NOT NULL,
    email                VARCHAR(100) NOT NULL UNIQUE,
    sala_de_atendimento  VARCHAR(50)  NOT NULL,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT now()
);
