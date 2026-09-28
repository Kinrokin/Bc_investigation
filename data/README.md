# Financial tables and provenance

These CSVs are preserved transcriptions from the collected dossier, not raw bank exports. Fiscal years in `history`, `revenue`, `expense`, `balance` and `cash` end June 30. Internal figures are management-use actuals/budget for the eight months ending February 28, 2026, not audited September cash.

Primary source S01: [67-page June 22 City packet](../sources/originals/City_June22_2026_Packet.pdf). Source page locators: CDBG chronology p6; ordinance p8; lease pp10–18; internal accounts pp31–40 (income statement p32); independent audit pp41–67; balance p46; activities p47; cash flow p49; going concern pp63–64; controls pp65–67. The full public packet is not the same thing as each email or receipt mentioned within it.

S02: [IRS-derived public filing series](https://projects.propublica.org/nonprofits/organizations/237116216). FY2024–FY2025 totals match the recovered financial audit. Full-return HTML views were obtained later and are labeled as derived renderings; no original IRS XML is claimed.

United Way calendar-year institutional allocations are distinct from Bartlett fiscal-year recognized revenue. Sources: the original 2024 and 2025 annual reports in `sources/originals`.

- `history.csv`: seven-year reported totals; not a transaction history.
- `revenue.csv`: exact component bridge; $321,135 government-grant decline not allocated by award.
- `expense.csv`: functional expense categories, not proof of propriety of each expenditure.
- `balance.csv`: lease accounting distinguished from unpaid operating obligations.
- `cash.csv`: FY2025 operating cash-flow components; not a dated bank ledger.
- `internal.csv`: eight-month management figures; actuals and budgets are different.
- `cdbg.csv`: City-recorded dates and amounts. Some reference dates are corrected submissions, not original receipt. Neither 14 nor 52 elapsed days alone adjudicates compliance.
- `uw.csv`: reported allocations/approvals, not all receipts or contract terms.
- `provisional_MAP.csv`: inherited browser transcriptions without independently checked program/vendor/claim crosswalk, reversals or settlement. Do not use to infer cause.

Derived arithmetic: `reconciliation_results.json`, built by `scripts/reconcile.py`. Candidate 3.5% pattern/four-cent carryover are hypotheses consistent with the reported numbers, not recovered ledger entries. No cash-exhaustion date or September payroll amount can be inferred from the February accounting deficit.
