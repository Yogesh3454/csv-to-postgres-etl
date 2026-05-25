-- ============================================
-- Schema: ETL Database for Sales Data
-- ============================================

-- Create database (run as superuser)
-- CREATE DATABASE etl_db;

-- Connect to etl_db before running below

-- Drop table if exists (for re-runs during development)
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS etl_logs;

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL UNIQUE,
    customer_name   VARCHAR(100) NOT NULL,
    product         VARCHAR(100) NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    order_date      DATE NOT NULL,
    status          VARCHAR(20) CHECK (status IN ('completed', 'pending', 'cancelled')),
    loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ETL audit log table
CREATE TABLE IF NOT EXISTS etl_logs (
    id              SERIAL PRIMARY KEY,
    run_id          VARCHAR(50) NOT NULL,
    run_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_name       VARCHAR(255),
    rows_extracted  INTEGER DEFAULT 0,
    rows_transformed INTEGER DEFAULT 0,
    rows_loaded     INTEGER DEFAULT 0,
    rows_failed     INTEGER DEFAULT 0,
    status          VARCHAR(20) CHECK (status IN ('SUCCESS', 'FAILED', 'PARTIAL')),
    error_message   TEXT
);

-- Useful views
CREATE OR REPLACE VIEW sales_summary AS
SELECT
    status,
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_items,
    ROUND(SUM(price * quantity), 2) AS total_revenue
FROM sales
GROUP BY status;
