-- =====================================================================
-- 06_github_actions.sql: let GitHub Actions connect as DBT_USER with its OWN key
-- Run in Snowsight, one section at a time. Rerunnable.
--
-- GitHub Actions (CI on pull requests and the daily production job) connects as the existing service user
-- DBT_USER with role TRANSFORMER, but with a second key pair made only for GitHub:
--   * RSA_PUBLIC_KEY   = your laptop's key (unchanged)
--   * RSA_PUBLIC_KEY_2 = GitHub's key (made by scripts/make_key_pair.py)
-- If GitHub's key ever leaks: section 4 removes it, and your laptop keeps working.
-- =====================================================================

-- ---------- 1. add GitHub's public key (paste the statement printed by make_key_pair.py) ----------
use role SECURITYADMIN;
-- alter user DBT_USER set rsa_public_key_2 = 'MIIBIjANBgkqh...';      <- the line printed by the script

-- ---------- 2. check: both fingerprints are set ----------
desc user DBT_USER;
select "property", "value"
from table(result_scan(last_query_id()))
where "property" in ('RSA_PUBLIC_KEY_FP', 'RSA_PUBLIC_KEY_2_FP', 'DEFAULT_ROLE', 'TYPE');
-- expect: RSA_PUBLIC_KEY_FP and RSA_PUBLIC_KEY_2_FP both start with SHA256:..., TYPE = SERVICE

-- ---------- 3. CI builds in throw-away schemas CI_PR_<number> ----------
-- TRANSFORMER already has CREATE SCHEMA on GODESI_ANALYTICS (Phase 1), so nothing new is needed.
-- List any CI schema left behind (should be empty: each CI run drops its own schema at the end):
use role TRANSFORMER;
show schemas like 'CI_PR_%' in database GODESI_ANALYTICS;

-- ---------- 4. revoke GitHub's access (only if the key leaks or the project ends) ----------
-- use role SECURITYADMIN;
-- alter user DBT_USER unset rsa_public_key_2;
