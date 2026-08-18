pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            // Zebra repositories (if needed)
            url = uri("https://jcenter.bintray.com")
        }
    }

    versionCatalogs {
        create("libs") {
            version("kotlin", "1.9.10")
            version("androidx-compose", "2024.01.00")
            version("androidx-lifecycle", "2.6.2")
            version("hilt", "2.48")
            version("okhttp", "4.11.0")
            version("retrofit", "2.9.0")

            plugin("android-application", "com.android.application").version("8.1.2")
            plugin("kotlin-android", "org.jetbrains.kotlin.android").version("1.9.10")
            plugin("kotlin-serialization", "org.jetbrains.kotlin.plugin.serialization").version("1.9.10")
            plugin("hilt-android", "com.google.dagger.hilt.android").version("2.48")
            plugin("kotlin-kapt", "org.jetbrains.kotlin.kapt").version("1.9.10")

            library("androidx-core", "androidx.core:core-ktx:1.12.0")
            library("androidx-appcompat", "androidx.appcompat:appcompat:1.6.1")
            library("androidx-lifecycle-runtime", "androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
            library("androidx-compose-ui", "androidx.compose.ui:ui:2024.01.00")
            library("androidx-compose-material3", "androidx.compose.material3:material3:1.1.2")
            library("androidx-compose-runtime", "androidx.compose.runtime:runtime:2024.01.00")

            library("okhttp", "com.squareup.okhttp3:okhttp:4.11.0")
            library("okhttp-logging", "com.squareup.okhttp3:logging-interceptor:4.11.0")
            library("retrofit", "com.squareup.retrofit2:retrofit:2.9.0")
            library("retrofit-kotlin-serialization", "com.jakewharton.retrofit:retrofit2-kotlinx-serialization-converter:1.0.0")

            library("hilt-android", "com.google.dagger:hilt-android:2.48")
            library("hilt-compiler", "com.google.dagger:hilt-compiler:2.48")

            library("timber", "com.jakewharton.timber:timber:5.0.1")

            library("junit", "junit:junit:4.13.2")
            library("androidx-test-junit", "androidx.test.ext:junit:1.1.5")
            library("androidx-test-espresso", "androidx.test.espresso:espresso-core:3.5.1")
            library("androidx-compose-test", "androidx.compose.ui:ui-test-junit4:2024.01.00")

            bundle("androidx-compose", listOf("androidx-compose-ui", "androidx-compose-material3", "androidx-compose-runtime"))
            bundle("androidx-lifecycle", listOf("androidx-lifecycle-runtime"))
            bundle("network", listOf("retrofit", "retrofit-kotlin-serialization", "okhttp", "okhttp-logging"))
        }
    }
}

rootProject.name = "IDataProject"
include(":app")
