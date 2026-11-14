-- prepare_similarity_search_service_db.sql
-- Runs against POSTGRES_DB (similarity_search_service_db) from docker-compose.yml

CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;