-- ============================================
-- GoDesi Analytics: role tests (step 1.9)
-- Run ONE statement at a time (Ctrl+Enter) and compare with the comment
-- ============================================

-- turn off secondary roles, otherwise your user keeps ALL its roles
-- and the "should FAIL" tests would wrongly pass
USE SECONDARY ROLES NONE;
USE WAREHOUSE GODESI_WH;

-- ---------- LOADER ----------
USE ROLE LOADER;
CREATE OR REPLACE TABLE GODESI_RAW.ERP.TEST_LOAD (id INT, name STRING);    -- PASS
INSERT INTO GODESI_RAW.ERP.TEST_LOAD VALUES (1, 'kaju katli');           -- PASS
SELECT * FROM GODESI_RAW.ERP.TEST_LOAD;                                  -- PASS
CREATE TABLE GODESI_ANALYTICS.MARTS.TEST_NOPE (id INT);                  -- FAIL (no access to analytics)

-- ---------- TRANSFORMER ----------
USE ROLE TRANSFORMER;
SELECT * FROM GODESI_RAW.ERP.TEST_LOAD;                                  -- PASS (FUTURE grant worked)
INSERT INTO GODESI_RAW.ERP.TEST_LOAD VALUES (2, 'mysore pak');           -- FAIL (RAW is read-only)
CREATE OR REPLACE TABLE GODESI_ANALYTICS.DBT_DEV_HEGDE.TEST_DEV AS SELECT 1 AS x;  -- PASS
CREATE OR REPLACE TABLE GODESI_ANALYTICS.MARTS.TEST_MART AS SELECT 1 AS x;         -- PASS

-- ---------- REPORTER ----------
USE ROLE REPORTER;
SELECT * FROM GODESI_ANALYTICS.MARTS.TEST_MART;                          -- PASS (FUTURE grant worked)
SELECT * FROM GODESI_ANALYTICS.DBT_DEV_HEGDE.TEST_DEV;                   -- FAIL (MARTS only)
SELECT * FROM GODESI_RAW.ERP.TEST_LOAD;                                  -- FAIL (no RAW access)

-- ---------- CLEAN UP ----------
USE ROLE TRANSFORMER;
DROP TABLE IF EXISTS GODESI_ANALYTICS.DBT_DEV_HEGDE.TEST_DEV;
DROP TABLE IF EXISTS GODESI_ANALYTICS.MARTS.TEST_MART;
USE ROLE LOADER;
DROP TABLE IF EXISTS GODESI_RAW.ERP.TEST_LOAD;

USE ROLE ACCOUNTADMIN;
USE SECONDARY ROLES ALL;   -- put your normal setting back