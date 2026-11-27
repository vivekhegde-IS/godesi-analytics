-- =====================================================================
-- 05_streamlit_app.sql: the GoDesi dashboard as a Streamlit app INSIDE Snowflake
-- Run in Snowsight, one section at a time. Rerunnable.
--
-- The app is owned by REPORTER and runs with REPORTER's rights, so it can only read MARTS
-- (least privilege, same as Power BI). It reads the marts live with the SQL in queries.py.
-- Cost: the app uses GODESI_WH while someone has it open; the warehouse auto-suspends after 60 s.
-- =====================================================================

-- ---------- 1. a schema for apps, and the rights REPORTER needs to own one ----------
use role SYSADMIN;
create schema if not exists GODESI_ANALYTICS.APPS comment = 'Streamlit apps (dashboard)';
grant usage on schema GODESI_ANALYTICS.APPS to role REPORTER;
grant create stage, create streamlit on schema GODESI_ANALYTICS.APPS to role REPORTER;

-- ---------- 2. a stage that holds the app's files ----------
use role REPORTER;
use warehouse GODESI_WH;
create stage if not exists GODESI_ANALYTICS.APPS.DASHBOARD_STAGE
    directory = (enable = true)
    comment = 'app.py, queries.py and environment.yml of the GoDesi dashboard';

-- ---------- 3. upload the 3 files (Snowsight UI, not SQL) ----------
-- Data > Databases > GODESI_ANALYTICS > APPS > Stages > DASHBOARD_STAGE > "+ Files"
-- upload from godesi-analytics\dashboard\streamlit\ :  app.py   queries.py   environment.yml
list @GODESI_ANALYTICS.APPS.DASHBOARD_STAGE;          -- expect the 3 files

-- ---------- 4. create the app from the stage ----------
create or replace streamlit GODESI_ANALYTICS.APPS.GODESI_DASHBOARD
    from '@GODESI_ANALYTICS.APPS.DASHBOARD_STAGE'
    main_file = 'app.py'
    query_warehouse = GODESI_WH
    title = 'GoDesi Sales & Distribution Analytics'
    comment = 'Executive overview, products, channels, customers, supply and market (Q1-Q9)';

show streamlits in schema GODESI_ANALYTICS.APPS;
-- Open it: Projects > Streamlit > "GoDesi Sales & Distribution Analytics"
-- The sidebar says "Live data from Snowflake MARTS".

-- ---------- after changing app.py: upload it again, then ----------
-- alter streamlit GODESI_ANALYTICS.APPS.GODESI_DASHBOARD commit;   -- only if Snowsight asks for it
