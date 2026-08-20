import com.android.build.gradle.internal.cxx.configure.gradleLocalProperties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.hilt.android)
    kotlin("kapt")
}

val localProps = gradleLocalProperties(rootDir, providers)

android {
    namespace = "com.idataproject"
    compileSdk = (rootProject.ext["compileSdkVersion"] as Int)

    defaultConfig {
        applicationId = "com.idataproject.rfidscanner"
        minSdk = (rootProject.ext["minSdkVersion"] as Int)
        targetSdk = (rootProject.ext["targetSdkVersion"] as Int)
        versionCode = 1
        versionName = "0.1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables { useSupportLibrary = true }
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            buildConfigField("String", "ODOO_BASE_URL", "\"http://10.0.2.2:8069\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // ODOO_BASE_URL for release is set via CI environment or local.properties
            buildConfigField(
                "String",
                "ODOO_BASE_URL",
                "\"${localProps.getProperty("odoo.base.url", "https://your-odoo-host")}\""
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }
    packaging {
        resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" }
    }
}

dependencies {
    // AndroidX core
    implementation(libs.androidx.core)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.lifecycle.runtime)

    // Jetpack Compose
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation(libs.bundles.androidx.compose)

    // Networking (Retrofit + OkHttp)
    implementation(libs.bundles.network)

    // Dependency Injection (Hilt)
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)

    // Logging
    implementation(libs.timber)

    // iData T1UHF SDK (to be added once SDK is sourced — Gate 1)
    // implementation(files("libs/idataT1UHF-sdk.aar"))

    // Unit tests
    testImplementation(libs.junit)

    // Instrumented tests
    androidTestImplementation(libs.androidx.test.junit)
    androidTestImplementation(libs.androidx.test.espresso)
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.01.00"))
    androidTestImplementation(libs.androidx.compose.test)
}
