plugins {
    id("com.android.application")
}

android {
    namespace = "com.cleanframe.onn"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.cleanframe.onn"
        // Google TV floor. coffey ships Android 14 (API 34).
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.7.0-onn.1"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Debug-signed for sideloading; replace before distributing.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        buildConfig = true
    }
}

/**
 * Upstream's web assets are fetched by tools/sync-upstream.sh, not committed.
 * Fail the build loudly if they are absent, rather than producing an APK that
 * boots to a blank screen on the TV.
 */
val checkUpstreamAssets by tasks.registering {
    val index = layout.projectDirectory.file("src/main/assets/web/index.html")
    doLast {
        if (!index.asFile.exists()) {
            throw GradleException(
                "Upstream CleanFrame assets are missing at app/src/main/assets/web/. " +
                    "Run tools/sync-upstream.sh first."
            )
        }
    }
}

tasks.named("preBuild").configure {
    dependsOn(checkUpstreamAssets)
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.webkit:webkit:1.12.1")
}
