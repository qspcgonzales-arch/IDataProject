# ProGuard rules for IDataProject RFID Scanner
# Keep Retrofit + Kotlin serialization models
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keep class okhttp3.** { *; }
-keep class kotlinx.serialization.** { *; }

# Keep Hilt generated classes
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }

# Keep data model classes (serialized to/from JSON)
-keep class com.idataproject.models.** { *; }

# iData T1UHF SDK (add specific keep rules once SDK is sourced)
# -keep class com.idata.** { *; }
