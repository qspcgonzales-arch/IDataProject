# stock_barcode_rfid — INACTIVE (superseded 2026-08-26)

This module implements the original Rev. 2 roadmap architecture:
a custom controller (`POST /stock_barcode_rfid/scan`) that resolves
EPCs server-side against `rfid.tag.mapping` and logs every scan to
`stock.barcode.rfid.scan`.

**As of 2026-08-26 this is no longer the active integration path.**
Per direction from the project owner, the Android app now talks to
Odoo directly via XML-RPC/JSON-RPC, matching EPCs against
`stock.lot.name` and writing `stock.quant`/`stock.move` itself. No
Odoo-side module is required for that flow.

This code is kept in version control rather than deleted, in case the
direction changes again. See Section 9 (Addendum — Architecture
Pivot) of `rfid-odoo-roadmap-MASTER.docx` for the full rationale and
the known limitation this pivot reintroduces (unmapped EPCs have no
defined path to being flagged for operator review under the new
approach).

Do not install this module in the pilot Odoo instance unless the
direction reverts back to the Section 2 architecture.
