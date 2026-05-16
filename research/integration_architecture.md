# Enterprise integration architecture — event contracts (stub)

Live connectivity to **Yardi**, **Salesforce**, **ERP**, and internal apps is **out of scope** for this synthetic repo. The artifact here is a **small, honest integration map**: stable keys and **event-shaped** payloads you would normalize into bronze before the medallion renewal features used in the demo.

Design goals: **idempotent ingestion**, **clear grain** (property / unit / lease / resident), and **replay** from event log or nightly snapshot.

## Canonical keys (examples)

| Concept | Stable id | Notes |
| --- | --- | --- |
| Property | `property_id` | Internal master id; map vendor `pcode` / `community_code` in bronze |
| Unit | `unit_id` | Surrogate; vendor unit + property composite if needed |
| Resident / household | `resident_household_id` | GDPR-sensitive; hash or tokenize in non-prod |
| Lease | `lease_id` | Version episodes (renewal, transfer) as separate rows with `lease_episode_seq` |
| Work order | `work_order_id` | Idempotent upsert |
| Lead / tour | `crm_lead_id` | Salesforce or CRM-agnostic |

## Event contracts

### 1. Rent roll snapshot

- **Trigger:** nightly batch or intraday delta feed.
- **Grain:** one row per **unit–occupancy** as of `as_of_date`.
- **Payload (illustrative):** `property_id`, `unit_id`, `lease_id`, `resident_household_id`, `move_in_date`, `lease_end_date`, `monthly_rent`, `market_rent`, `concession_amount`, `ledger_balance`, `as_of_date`, `source_system`, `ingest_batch_id`.

### 2. Lease signed / renewed

- **Trigger:** document execution or e-sign completion.
- **Payload:** `lease_id`, `property_id`, `unit_id`, `lease_start_date`, `lease_end_date`, `term_months`, `monthly_rent`, `renewal_flag`, `prior_lease_id`, `signed_at`, `source_system`.

### 3. Renewal offer

- **Trigger:** offer generated or sent.
- **Payload:** `lease_id`, `offer_id`, `offer_rent`, `offer_effective_date`, `offer_expiry_date`, `channel` (email / portal / agent), `created_at`.

### 4. Work order

- **Trigger:** create, status change, complete.
- **Payload:** `work_order_id`, `property_id`, `unit_id`, `category`, `priority`, `status`, `opened_at`, `completed_at`, `vendor_id` (optional).

### 5. Tour / lead stage

- **Trigger:** CRM stage change or activity log.
- **Payload:** `crm_lead_id`, `property_id`, `stage` (e.g. tour_scheduled, applied, approved), `stage_changed_at`, `channel`, `campaign_id` (optional).

### 6. Payment delinquency

- **Trigger:** nightly AR aging or ledger posting.
- **Payload:** `lease_id`, `as_of_date`, `days_past_due`, `amount_past_due`, `last_payment_date`, `source_system`.

## Bronze → silver

- See [`integration_field_dictionary.template.csv`](integration_field_dictionary.template.csv) (multi-line CSV) and the human-readable mirror [`integration_field_dictionary.md`](integration_field_dictionary.md).
- Join on **keys** and time windows to build `lease_episode_features`-style rows; keep **source lineage** columns for audit.

## Out of scope (explicit)

- OAuth / API credentials, real endpoint URLs, and PII-bearing sample payloads are **not** stored in git.
