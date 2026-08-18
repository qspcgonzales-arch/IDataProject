# Android RFID Scanner App

Kotlin-based Android app for Zebra T1/T2 UHF handheld scanners.

## Quick Start

### Prerequisites
- Android Studio (2024.1+)
- JDK 17+
- Android SDK 31+ (target 34)
- Zebra UHF SDK (download from Zebra developer portal)

### Setup

```bash
# Navigate to android directory
cd android

# Configure Android SDK path (if needed)
# Edit local.properties:
# sdk.dir=/path/to/android-sdk

# Build the app
./gradlew build

# Run unit tests
./gradlew test

# Run on device/emulator (requires connected device)
./gradlew installDebug

# Connect to running app
adb logcat | grep "IDataProject"
```

## Project Structure

```
app/
├── build.gradle.kts                 # App-level build config
├── src/
│   ├── main/
│   │   ├── kotlin/com/idataproject/
│   │   │   ├── MainActivity.kt       # Main activity & entry point
│   │   │   ├── scanner/
│   │   │   │   ├── ZebraUHFReader.kt # Zebra UHF reader wrapper
│   │   │   │   └── ScannerManager.kt # Manages scan loop
│   │   │   ├── ui/
│   │   │   │   ├── screens/          # Compose screens
│   │   │   │   └── components/       # Reusable Compose components
│   │   │   ├── network/
│   │   │   │   └── OdooClient.kt     # HTTP client for Odoo API
│   │   │   ├── storage/
│   │   │   │   └── SecurePreferences.kt  # Keystore for API keys
│   │   │   ├── models/
│   │   │   │   └── ScanEvent.kt      # Data classes
│   │   │   └── viewmodel/
│   │   │       └── ScannerViewModel.kt   # UI state management
│   │   ├── res/
│   │   │   ├── values/
│   │   │   │   ├── strings.xml
│   │   │   │   └── colors.xml
│   │   │   └── layout/
│   │   └── AndroidManifest.xml
│   ├── test/
│   │   └── kotlin/...                # Unit tests (no device needed)
│   └── androidTest/
│       └── kotlin/...                # Integration tests (device needed)
└── proguard-rules.pro                # ProGuard obfuscation rules

gradle/                               # Gradle wrapper
build.gradle.kts                      # Root build config
settings.gradle.kts                   # Project settings
```

## Conventions

- **Language:** Kotlin (prefer idiomatic style over Java patterns)
- **Async:** Suspend functions + coroutines (not callbacks)
- **Architecture:** MVVM with Compose for UI
- **Naming:** `camelCase` for functions/variables, `PascalCase` for classes
- **Logging:** `Log.d()` for debug, `Log.e()` for errors
- **Comments:** Explain WHY, not WHAT (code should be self-documenting)

Example:
```kotlin
class ScannerViewModel : ViewModel() {
    private val _scans = MutableStateFlow<List<ScanEvent>>(emptyList())
    val scans: StateFlow<List<ScanEvent>> = _scans.asStateFlow()

    fun startScanning() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                scanner.startInventory()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start scan", e)
            }
        }
    }
}
```

## Dependencies

Key libraries (see `build.gradle.kts` for full list):

```
// Coroutines
kotlinx-coroutines-android

// UI (Jetpack Compose)
androidx-compose-ui
androidx-compose-material3

// Networking
okhttp3
retrofit2

// Security
androidx-security-crypto  # For Keystore

// Testing
junit4
androidx-test-junit

// Logging
timber  # Better logging than Log
```

## Testing

### Unit Tests (fast, no device)
```bash
./gradlew test
```

### Integration Tests (on device/emulator)
```bash
./gradlew connectedAndroidTest
```

### Manual Testing Checklist
- [ ] App starts, login screen appears
- [ ] Enter Odoo URL + API key, login succeeds
- [ ] Scan 10 tags, each appears in UI
- [ ] Scan duplicate tag within 2sec, app dedupes locally
- [ ] Turn off Wi-Fi, scan 5 tags, turn on Wi-Fi, all 5 arrive in Odoo
- [ ] Calibration profile downloads successfully
- [ ] Operator can see live tag count during scan

## Debugging

### Logcat
```bash
./gradlew connectedAndroidTest --info
# OR
adb logcat | grep "IDataProject"
```

### Android Studio Debugger
- Set breakpoint, run in debug mode
- Inspect variables in Debug pane
- Evaluate expressions in console

### Network Traffic (Charles/Fiddler)
- Intercept Odoo API calls
- Verify POST body, response headers

## Building for Release

```bash
# Sign APK (requires keystore)
./gradlew assembleRelease -Pandroid.injected.signing.store.file=~/keystore.jks

# Check APK size & dependencies
./gradlew bundleRelease
./gradlew dependency-check  # Security check
```

## Common Issues

**Build fails: "Zebra SDK not found"**
- Download Zebra UHF SDK from developer portal
- Extract to `android/libs/`
- Reference in `build.gradle.kts`

**Emulator doesn't have Wi-Fi**
- Emulator needs internet for API calls
- Use AVD Manager to configure network
- Or test on real device with Wi-Fi

**ProGuard obfuscation breaks app**
- Add exceptions in `proguard-rules.pro`
- Test release build on device before shipping

See DEVELOPMENT.md for more troubleshooting.

## Performance Targets

- Scan loop: ≥20 tags/sec
- Local dedup: <1ms per EPC
- POST to Odoo: batch 10 EPCs per 500ms
- Memory baseline: <100MB
- Battery: minimal drain during 1-hour shelf scan

## Security

- API key stored in Android Keystore (hardware-backed if available)
- HTTPS + certificate pinning to Odoo server
- No secrets in logs or crash reports
- ProGuard obfuscation enabled in release builds

See SECURITY.md for full details.

## Resources

- [Zebra UHF SDK Docs](https://www.zebra.com/en/us/solutions/mobile-computing.html)
- [Android Documentation](https://developer.android.com/)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-overview.html)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)
