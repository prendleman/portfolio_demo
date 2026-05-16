# Integration field dictionary (readable)

Machine-editable source of truth: [`integration_field_dictionary.template.csv`](integration_field_dictionary.template.csv) (one row per field — **always use newline-terminated rows** in editors and PRs so GitHub does not collapse the file).

Below is the same **sample** contract in markdown for reviewers who never open CSV.

| entity | source_system | field_key | description | pii_class | refresh_cadence | idempotency_key_example |
| --- | --- | --- | --- | --- | --- | --- |
| lease | yardi | LeaseId | Internal lease identifier | — | daily | `LeaseId` + `as_of_date` |
| lease | yardi | LeaseFromDate | Lease start | — | daily | `LeaseId` |
| lease | yardi | LeaseToDate | Lease end / expiration | — | daily | `LeaseId` |
| lease | yardi | MonthlyRent | Contract rent | — | daily | `LeaseId` + `as_of_date` |
| resident_token | salesforce | ContactId | CRM contact key (hash in bronze) | PII_hash_only | daily | `ContactId` |
| resident_token | salesforce | HouseholdId | Household / guarantor grouping | PII_hash_only | daily | `HouseholdId` |
| lead | salesforce | OpportunityId | Sales / nurture opportunity | — | hourly | `OpportunityId` |
| lead | salesforce | StageName | Pipeline stage (tour, applied, approved) | — | hourly | `OpportunityId` + `StageName` + `LastStageChange` |
| tour | salesforce | EventId | Tour / visit activity | — | hourly | `EventId` |
| property | yardi | PropertyId | Property / community master key | — | daily | `PropertyId` |
| property | yardi | PropertyCode | Vendor community code | — | daily | `PropertyCode` |
| unit | yardi | UnitId | Physical unit key | — | daily | `UnitId` + `PropertyId` |
| unit | yardi | UnitNumber | Marketing unit number | — | daily | `PropertyId` + `UnitNumber` |
| rent_roll | yardi | AsOfDate | Snapshot date for occupancy / rent | — | daily | `PropertyId` + `AsOfDate` |
| rent_roll | yardi | OccupancyStatus | Occupied / notice / vacant | — | daily | `UnitId` + `AsOfDate` |
| work_order | yardi | WorkOrderId | Maintenance work order | — | hourly | `WorkOrderId` |
| work_order | yardi | Category | WO category (HVAC, plumbing, …) | — | hourly | `WorkOrderId` |
| work_order | yardi | Status | Open / complete | — | hourly | `WorkOrderId` + `Status` + `ChangedAt` |
| payment | erp | VendorInvoiceId | AP / cash application row | — | daily | `VendorInvoiceId` |
| payment | erp | AmountPosted | Payment or charge amount | — | daily | `VendorInvoiceId` + `LedgerLineId` |
| payment | erp | DaysPastDue | Derived delinquency signal | — | daily | `LeaseId` + `AsOfDate` |
| renewal_offer | internal | OfferId | Renewal offer artifact | — | hourly | `OfferId` |
| renewal_offer | internal | LeaseId | Target lease | — | hourly | `OfferId` |

See also [`integration_architecture.md`](integration_architecture.md) for **event** shapes (rent roll snapshot, lease signed, etc.).
