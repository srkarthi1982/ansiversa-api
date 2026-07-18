# Bill Splitter Destination

Destination Status: approved
Current Journey Progress: 20 / 100
Reviewed At: 2026-07-18

Bill Splitter handles a single short-lived bill through a draft shell, unique participants, item lines, equal/single/custom item allocations, bill-level discount/tax/service/tip, deterministic cent reconciliation, recorded paid amounts, and settlement status. It is distinct from recurring household accounting.

All money uses two-decimal server-side `Decimal` arithmetic and fixed-precision database columns. Equal split remainder cents go to participant sort order. Bill-level adjustments are distributed by the same rule. Overpayment is rejected. No payment transfer, banking, debt collection, OCR, AI, exchange conversion, invoicing, advice, or compliance claims.

## Promotion

Approved live at version `1.0.0` after Astra review, Partner manual verification, production-configured isolated migration verification, Apps row promotion, destination metadata sync, overview metadata sync, and validation.
