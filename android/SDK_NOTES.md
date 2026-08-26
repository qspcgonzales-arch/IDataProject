# RFID Hardware SDK — source and rationale

Three vendor SDK zips were provided by IT with no indication of which
matches the iData T1UHF handheld. After inspecting contents (not just
filenames), here's what's actually in each and what's in use.

## In use: `UHF开发包_V2.2` → `app/libs/UHFJar_V1.4.05.aar`

The only one of the three explicitly titled **"iData UHF Module
Interface Document"** in its own docs. Includes:
- `UHFJar_V1.4.05.aar` (2024-05) — the Java API, now in `app/libs/`
- `libjni_rfid_driver.so` + `libserialportJni.so` for arm64-v8a and
  armeabi-v7a — now in `app/src/main/jniLibs/`
- A working demo (`UHFDemo`) with multiple dated, built release APKs
  (v1.2.534, 2024-05-09/11) — strongest signal this SDK is actually
  functional, not just scaffolding
- Docs reference a "50P" handheld with a "Q5000" UHF trigger module —
  **check the physical device for these model markings** to confirm
  this is really the T1UHF unit; "T1UHF" doesn't appear verbatim
  anywhere in any of the three SDKs

**Known gap:** no x86/x86_64 native libs included, so this won't run
on the Android Studio emulator — ARM hardware (real device) only.

## Not in use, kept as fallback: `RFID_SDK_20250319`

Generic UHF module API (`rfid.uhfapi.jar`) bundled with a separate,
explicitly different-model demo ("Y2007" handheld). Does include
x86/x86_64 native libs (`libserial_port.so`), but these are **not
drop-in compatible** with UHFJar_V1.4.05's native layer — different
library name, different JNI package (`rfid.uhfapi` vs `com.uhf`).
Copying them in without testing would risk `UnsatisfiedLinkError` at
runtime. Only worth revisiting if UHFJar_V1.4.05 turns out to be the
wrong SDK for the actual device.

## Excluded entirely: `iScanPro_iScanPlus_SDK`

This is a barcode/OCR scanner SDK (2D barcode + camera image/video
stream), not a UHF RFID reader. Wrong hardware category — not
relevant to this project regardless of which handheld is confirmed.
