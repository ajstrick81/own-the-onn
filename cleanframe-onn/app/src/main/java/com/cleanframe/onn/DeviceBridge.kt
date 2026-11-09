package com.cleanframe.onn

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.util.Log
import android.webkit.JavascriptInterface
import org.json.JSONArray
import org.json.JSONObject

/**
 * The Android half of CleanFrame's platform seam.
 *
 * Upstream `app/device.js` exposes nine methods on `window.FrameDevice`, backed
 * by Tizen's `tizen.application` / `tizen.tvwindow` APIs. This class provides the
 * equivalent capabilities for Google TV, and `assets/platform/device.js` adapts
 * them back into the exact `FrameDevice` shape so `main.js` is untouched.
 *
 * Every method is invoked by WebView on a private binder thread, never the main
 * thread. Reads of PackageManager are thread-safe; anything that starts an
 * Activity is posted to the main looper, so results are reported by resolving
 * the Intent up front rather than by waiting on the launch itself.
 */
class DeviceBridge(private val context: Context) {

    private val main = Handler(Looper.getMainLooper())
    private val pm: PackageManager get() = context.packageManager

    /** Hidden from the grid: this launcher, and the stock launcher it replaces. */
    private val suppressed = setOf(
        BuildConfig.APPLICATION_ID,
        "com.google.android.apps.tv.launcherx",
        "com.google.android.tvlauncher",
        "com.google.android.tungsten.setupwraith"
    )

    /** Upstream brand ids mapped to the package serving that brand on Google TV. */
    private val brandPackages = mapOf(
        "netflix" to "com.netflix.ninja",
        "youtube" to "com.google.android.youtube.tv",
        "disneyplus" to "com.disney.disneyplus",
        "primevideo" to "com.amazon.amazonvideo.livingroom",
        "appletv" to "com.apple.atve.androidtv.appletv",
        "applemusic" to "com.apple.android.music",
        "spotify" to "com.spotify.tv.android",
        "stremio" to "com.stremio.one",
        "tubi" to "com.tubitv",
        "hbomax" to "com.wbd.stream",
        "abciview" to "au.net.abc.iview",
        "sbs" to "au.com.sbs.ondemand.tv"
    )

    /** Reverse map, so a discovered package can be tagged with its brand icon. */
    private val packageBrands = brandPackages.entries.associate { (k, v) -> v to k }

    // ---------------------------------------------------------------- discovery

    /**
     * Installed, launchable apps as a JSON array of
     * `{ appId, name, brand, icon, rank }` -- the shape upstream's `apps()`
     * resolves with. Leanback entries rank ahead of phone-only ones, which is
     * the closest analogue to upstream's primary/streaming/other tiers.
     */
    @JavascriptInterface
    fun listApps(): String {
        val out = JSONArray()
        val seen = HashSet<String>()

        fun collect(category: String, baseRank: Int) {
            val intent = Intent(Intent.ACTION_MAIN).addCategory(category)
            val flags = PackageManager.MATCH_DEFAULT_ONLY
            for (info in pm.queryIntentActivities(intent, flags)) {
                val pkg = info.activityInfo?.packageName ?: continue
                if (pkg in suppressed || !seen.add(pkg)) continue
                val label = runCatching { info.loadLabel(pm).toString() }
                    .getOrNull()?.takeIf { it.isNotBlank() } ?: continue
                val brand = packageBrands[pkg] ?: ""
                out.put(
                    JSONObject()
                        .put("appId", pkg)
                        .put("name", label)
                        .put("brand", brand)
                        // Served by IconPathHandler rather than inlined as a
                        // data: URI, to keep the JS payload small on a slow box.
                        // Must stay ROOT-RELATIVE: main.js safeIcon() accepts
                        // only ^/[^/], file:/// or wgt-package:/// and silently
                        // drops an absolute https URL.
                        .put("icon", "/icon/$pkg.png")
                        .put("rank", if (brand.isNotEmpty()) baseRank else baseRank + 10)
                )
            }
        }

        collect(Intent.CATEGORY_LEANBACK_LAUNCHER, 0)
        collect(Intent.CATEGORY_LAUNCHER, 20)
        return out.toString()
    }

    // ------------------------------------------------------------------ launch

    /** Launch by package name. Returns an empty string on success, else a JSON error. */
    @JavascriptInterface
    fun launchPackage(packageName: String?): String {
        if (packageName.isNullOrBlank()) return error("This app has no launch target.")
        val intent = leanbackOrMainIntent(packageName)
            ?: return error(
                "That app is not installed on this device.",
                "CleanFrame found no launcher entry for $packageName."
            )
        return start(intent)
    }

    /** Launch by upstream brand id, mapping Samsung brands to Google TV packages. */
    @JavascriptInterface
    fun launchBrand(brand: String?): String {
        val pkg = brandPackages[brand] ?: return error("This app has no launch target.")
        return launchPackage(pkg)
    }

    /** The system home screen this launcher replaces, as an explicit escape hatch. */
    @JavascriptInterface
    fun openSystemHome(): String {
        for (pkg in listOf("com.google.android.apps.tv.launcherx", "com.google.android.tvlauncher")) {
            val intent = leanbackOrMainIntent(pkg) ?: continue
            return start(intent)
        }
        return error(
            "The Google TV home screen is not available.",
            "Its launcher package may be disabled on this device."
        )
    }

    /** Android TV settings, in place of Samsung's `com.samsung.tv.coba.setting`. */
    @JavascriptInterface
    fun openSettings(): String {
        val candidates = listOf(
            Intent(Settings.ACTION_SETTINGS),
            Intent("com.android.tv.settings.ACTION_SETTINGS")
        )
        for (intent in candidates) {
            if (intent.resolveActivity(pm) != null) return start(intent)
        }
        return error("The TV settings screen could not be opened.")
    }

    /**
     * Nearest analogue to Samsung Art Mode: the Google TV screensaver settings.
     *
     * The Onn is a streamer with no Art Mode and no panel of its own, so this
     * deliberately opens the ambient/screensaver configuration rather than
     * pretending to enter a display mode that does not exist here.
     */
    @JavascriptInterface
    fun openAmbient(): String {
        val candidates = listOf(
            Intent("android.settings.DREAM_SETTINGS"),
            Intent(Settings.ACTION_DISPLAY_SETTINGS)
        )
        for (intent in candidates) {
            if (intent.resolveActivity(pm) != null) return start(intent)
        }
        return error(
            "This device has no ambient screen setting.",
            "The Onn streamer has no Art Mode equivalent."
        )
    }

    // ------------------------------------------------------------------ inputs

    /**
     * Always an empty list.
     *
     * Upstream switches the TV's HDMI inputs through `tizen.tvwindow`. The Onn
     * 4K Plus is an HDMI *source* with no inputs of its own, so there is nothing
     * to enumerate. device.js reads the empty list and hides the inputs row.
     */
    @JavascriptInterface
    fun listSources(): String = JSONArray().toString()

    // ----------------------------------------------------------------- helpers

    /** Prefer a leanback entry, fall back to the phone launcher entry. */
    private fun leanbackOrMainIntent(packageName: String): Intent? {
        runCatching { pm.getLeanbackLaunchIntentForPackage(packageName) }
            .getOrNull()?.let { return it }
        runCatching { pm.getLaunchIntentForPackage(packageName) }
            .getOrNull()?.let { return it }
        return null
    }

    /**
     * Post an Activity start to the main thread.
     *
     * Resolvability is checked synchronously so the caller gets a truthful
     * answer without the WebView thread blocking on the launch itself.
     */
    private fun start(intent: Intent): String {
        if (intent.resolveActivity(pm) == null) {
            return error("That screen is not available on this device.")
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        main.post {
            runCatching { context.startActivity(intent) }
                .onFailure { Log.w(TAG, "Launch failed for " + (intent.action ?: "component"), it) }
        }
        return ""
    }

    private fun error(message: String, detail: String? = null): String =
        JSONObject().put("message", message).apply {
            if (detail != null) put("detail", detail)
        }.toString()

    private companion object {
        const val TAG = "CleanFrameBridge"
    }
}
