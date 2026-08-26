package com.idataproject.scanner

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/**
 * Local audit log for EPCs that don't resolve against Odoo.
 *
 * Context: the project's integration path is direct XML-RPC/JSON-RPC
 * from this app to Odoo (Desktop 1's "Option 3", see the roadmap's
 * Section 9 addendum, 2026-08-26). That approach matches EPCs against
 * stock.lot.name and has no server-side model to flag an unmapped EPC
 * with status='unknown' the way the original stock_barcode_rfid module
 * did. This class re-implements that missing piece on the app side:
 * every EPC the Odoo lookup fails to match gets logged here so an
 * operator can review and resolve it later, instead of the tag being
 * silently dropped.
 *
 * Wire this in wherever the real XML-RPC scan loop lives: on a lookup
 * returning no matching stock.lot, call logUnresolved(epc) before
 * discarding the scan.
 */
class UnresolvedScanStore(context: Context) :
    SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE $TABLE_NAME (
                $COL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COL_EPC TEXT NOT NULL,
                $COL_SCANNED_AT INTEGER NOT NULL,
                $COL_SESSION_ID TEXT,
                $COL_RESOLVED INTEGER NOT NULL DEFAULT 0,
                $COL_SYNCED INTEGER NOT NULL DEFAULT 0
            )
            """.trimIndent()
        )
        db.execSQL("CREATE INDEX idx_unresolved_epc ON $TABLE_NAME($COL_EPC)")
        db.execSQL("CREATE INDEX idx_unresolved_flag ON $TABLE_NAME($COL_RESOLVED)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS $TABLE_NAME")
        onCreate(db)
    }

    /**
     * Log an EPC that had no matching stock.lot in Odoo. Never throws
     * on a duplicate scan of the same unresolved EPC — every attempt
     * is recorded so an operator can see how often a given tag keeps
     * failing to resolve.
     */
    fun logUnresolved(epc: String, sessionId: String? = null): Long {
        val values = ContentValues().apply {
            put(COL_EPC, epc)
            put(COL_SCANNED_AT, System.currentTimeMillis())
            put(COL_SESSION_ID, sessionId)
            put(COL_RESOLVED, 0)
            put(COL_SYNCED, 0)
        }
        return writableDatabase.insert(TABLE_NAME, null, values)
    }

    /** All unresolved EPCs still awaiting operator review, most recent first. */
    fun getPendingReview(): List<UnresolvedScan> {
        val results = mutableListOf<UnresolvedScan>()
        val cursor = readableDatabase.query(
            TABLE_NAME,
            null,
            "$COL_RESOLVED = 0",
            null,
            null,
            null,
            "$COL_SCANNED_AT DESC",
        )
        cursor.use {
            while (it.moveToNext()) {
                results.add(
                    UnresolvedScan(
                        id = it.getLong(it.getColumnIndexOrThrow(COL_ID)),
                        epc = it.getString(it.getColumnIndexOrThrow(COL_EPC)),
                        scannedAt = it.getLong(it.getColumnIndexOrThrow(COL_SCANNED_AT)),
                        sessionId = it.getString(it.getColumnIndexOrThrow(COL_SESSION_ID)),
                    )
                )
            }
        }
        return results
    }

    /** Mark an EPC as manually resolved by an operator (e.g. mapped to a product). */
    fun markResolved(id: Long) {
        val values = ContentValues().apply { put(COL_RESOLVED, 1) }
        writableDatabase.update(TABLE_NAME, values, "$COL_ID = ?", arrayOf(id.toString()))
    }

    fun countPendingReview(): Int {
        readableDatabase.rawQuery(
            "SELECT COUNT(*) FROM $TABLE_NAME WHERE $COL_RESOLVED = 0",
            null,
        ).use { cursor ->
            cursor.moveToFirst()
            return cursor.getInt(0)
        }
    }

    companion object {
        private const val DATABASE_NAME = "unresolved_scans.db"
        private const val DATABASE_VERSION = 1
        private const val TABLE_NAME = "unresolved_scans"
        private const val COL_ID = "_id"
        private const val COL_EPC = "epc"
        private const val COL_SCANNED_AT = "scanned_at"
        private const val COL_SESSION_ID = "session_id"
        private const val COL_RESOLVED = "resolved"
        private const val COL_SYNCED = "synced"
    }
}

data class UnresolvedScan(
    val id: Long,
    val epc: String,
    val scannedAt: Long,
    val sessionId: String?,
)
