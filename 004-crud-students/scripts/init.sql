-- Schema for the students CRUD service.
-- Mounted at /docker-entrypoint-initdb.d/init.sql so the postgres image runs it
-- on first boot. Re-applied manually to additional databases (e.g. the test DB).

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'course_code') THEN
        CREATE TYPE course_code AS ENUM ('GES', 'GEC', 'GEB', 'GEP');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS students (
    id          TEXT        PRIMARY KEY,
    name        TEXT        NOT NULL,
    email       TEXT        NOT NULL UNIQUE,
    course      course_code NOT NULL,
    matricula   INTEGER     NOT NULL,
    active      BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (course, matricula)
);

CREATE SEQUENCE IF NOT EXISTS seq_matricula_ges START 1;
CREATE SEQUENCE IF NOT EXISTS seq_matricula_gec START 1;
CREATE SEQUENCE IF NOT EXISTS seq_matricula_geb START 1;
CREATE SEQUENCE IF NOT EXISTS seq_matricula_gep START 1;
