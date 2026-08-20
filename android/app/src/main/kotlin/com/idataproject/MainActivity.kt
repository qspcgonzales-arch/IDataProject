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
 * Implementation is scheduled across the following tracker windows:
 * - Aug 24–28 (Foundation): Android project structure + SDK validation
 * - Aug 31–Sep 10 (Scan Bridge): Retrofit/OkHttp API client, API key storage
 * - Sep 11–18 (Live RFID): iData T1UHF SDK inventory loop, live count UI
 * - Sep 21–30 (Calibration): Calibration profile selector, offline queue
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
 * TODO (Aug 31): Replace with real scan UI once Odoo bridge is live.
 */
@Composable
fun IDataProjectApp(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("IDataProject — RFID Scanner")
        Text("Scaffold ready — implementation begins Aug 24")
        Text("")
        Text("TODO:")
        Text("• Aug 24–28: Verify SDK + Odoo environment")
        Text("• Aug 31–Sep 10: Odoo bridge API client")
        Text("• Sep 11–18: iData T1UHF inventory loop")
        Text("• Sep 21–30: Calibration profiles")
    }
}
