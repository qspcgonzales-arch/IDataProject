package com.idataproject

import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel


/**
 * Main activity for IDataProject RFID Scanner app.
 *
 * Integration path (2026-08-26): direct XML-RPC/JSON-RPC calls to
 * Odoo, matching EPCs against stock.lot.name (Desktop 1's "Option 3",
 * see rfid-odoo-roadmap-MASTER.docx Section 9 addendum). EPCs with no
 * matching stock.lot are logged via UnresolvedScanStore instead of
 * being silently dropped, since this integration path has no
 * server-side status='unknown' model to fall back on.
 *
 * Phases:
 * - Phase 1: Scaffold (this file)
 * - Phase 2: Connect to Odoo API directly (XML-RPC/JSON-RPC)
 * - Phase 3: Integrate iData T1UHF reader (hardware SDK)
 * - Phase 4+: Implement full scanning and calibration UI
 */
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            IDataProjectApp()
        }
    }
}


/**
 * Main composable for the app.
 * TODO: Replace with actual UI implementation
 */
@Composable
fun IDataProjectApp(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("IDataProject — RFID Scanner")
        Text("Phase 1: Scaffold (in development)")
        Text("")
        Text("TODO:")
        Text("• Phase 2: Direct XML-RPC/JSON-RPC bridge to Odoo")
        Text("• Phase 3: iData T1UHF reader integration")
        Text("• Phase 4: Calibration profiles")
        Text("• Phase 5+: Full scanner UI + unresolved-EPC review screen")
    }
}
