// AGP 9 has built-in Kotlin support; the separate kotlin.android plugin is
// no longer applied (and is rejected if it is).
plugins {
    id("com.android.application") version "9.1.0" apply false
}
