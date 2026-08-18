plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.hilt.android) apply false
}

// Root-level build configuration shared across modules
ext {
    set("minSdkVersion", 31)
    set("targetSdkVersion", 34)
    set("compileSdkVersion", 34)
    set("kotlinVersion", "1.9.10")
}
