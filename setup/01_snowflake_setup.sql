-- ============================================
-- GoDesi Analytics: Snowflake setup
-- ============================================
-- GoDesi Analytics: Snowflake setup
-- Rerunnable: safe to run multiple times
-- ============================================

-- 1. WAREHOUSE        (role: SYSADMIN)

USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS GODESI_WH
    WITH
    WAREHOUSE_SIZE      = 'XSMALL'
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT             = 'Compute for GoDesi: loading, dbt builds and dashboards';

-- 2. DATABASES        (role: SYSADMIN)
USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS GODESI_RAW
    COMMENT = 'Bronze layer: untouched source data, loaded as-is';

CREATE DATABASE IF NOT EXISTS GODESI_ANALYTICS
    COMMENT = 'Silver and gold layers: models built by dbt';


-- 3. SCHEMAS          (role: SYSADMIN)
USE ROLE SYSADMIN;

-- raw (bronze): one schema per source system
CREATE SCHEMA IF NOT EXISTS GODESI_RAW.ERP             COMMENT = 'Products, distributors, stores, promotions, offline orders';
CREATE SCHEMA IF NOT EXISTS GODESI_RAW.ECOM            COMMENT = 'D2C website customers and orders';
CREATE SCHEMA IF NOT EXISTS GODESI_RAW.MARKETPLACE     COMMENT = 'Amazon, Flipkart and quick-commerce orders';
CREATE SCHEMA IF NOT EXISTS GODESI_RAW.INVENTORY       COMMENT = 'Daily warehouse stock levels';
CREATE SCHEMA IF NOT EXISTS GODESI_RAW.OPEN_FOOD_FACTS COMMENT = 'Real product data from Open Food Facts (ODbL)';

-- analytics (silver/gold): one schema per dbt layer, plus a dev sandbox
CREATE SCHEMA IF NOT EXISTS GODESI_ANALYTICS.DBT_DEV_PAI  COMMENT = 'Personal dev sandbox for dbt';
CREATE SCHEMA IF NOT EXISTS GODESI_ANALYTICS.STAGING      COMMENT = 'Silver: cleaned 1:1 source models';
CREATE SCHEMA IF NOT EXISTS GODESI_ANALYTICS.INTERMEDIATE COMMENT = 'Silver: joined and enriched models';
CREATE SCHEMA IF NOT EXISTS GODESI_ANALYTICS.MARTS        COMMENT = 'Gold: star schema and business marts for BI';
CREATE SCHEMA IF NOT EXISTS GODESI_ANALYTICS.SNAPSHOTS    COMMENT = 'Price history (SCD Type 2)';
-- 4. ROLES            (role: USERADMIN)

-- 5. GRANTS           (role: SECURITYADMIN)

-- 6. DBT SERVICE USER (role: USERADMIN)

-- 7. RESOURCE MONITOR (role: ACCOUNTADMIN)

-- 8. VERIFICATION