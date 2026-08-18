package com.idataproject

import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.activity.compose.setContent
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
 * Phases:
 * - Phase 1: Scaffold (this file)
 * - Phase 2: Connect to Odoo API
 * - Phase 3: Integrate Zebra UHF reader
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
        Text("• Phase 2: Odoo RFID bridge module")
        Text("• Phase 3: Zebra UHF reader integration")
        Text("• Phase 4: Calibration profiles")
        Text("• Phase 5+: Full scanner UI")
    }
}
