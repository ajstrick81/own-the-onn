package com.cleanframe.onn

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.util.Log
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent

/**
 * Makes CleanFrame the home screen on a device whose HOME intent it cannot win.
 *
 * On coffey the HOME resolver ranks by intent-filter priority, and only system
 * packages may declare one above 0:
 *
 *     launcherx HomeActivity          priority  2
 *     setupwraith RecoveryActivity    priority  1
 *     CleanFrame                      priority  0
 *
 * Disabling the stock launcher therefore hands HOME to the setup wizard's
 * recovery screen, not to CleanFrame (docs/install.md), and disabling that as
 * well means gutting the device's recovery path. This service takes the other
 * route and leaves every system package enabled:
 *
 *  1. The HOME key is claimed before the system acts on it, and opens
 *     CleanFrame instead.
 *  2. Whenever the stock home screen comes to the front anyway -- after boot,
 *     or when BACK exits the last app -- CleanFrame is brought over it.
 *
 * Nothing here is irreversible: turning the service off in
 * Settings > System > Accessibility restores stock behaviour at once.
 */
class HomeGuardService : AccessibilityService() {

    private var homeDownAt = 0L

    /**
     * Both halves of the press are consumed, so the system never sees HOME and
     * never opens the stock home screen. Consuming only the release is not an
     * option: the input dispatcher would never see the key come up and would
     * synthesise repeats forever.
     *
     * Because the system no longer sees the key, its own long-press HOME action
     * is gone too. Long-press is reused as the way back to the Google TV home
     * screen, so that screen stays one gesture away.
     */
    override fun onKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode != KeyEvent.KEYCODE_HOME) return false
        when (event.action) {
            KeyEvent.ACTION_DOWN -> if (event.repeatCount == 0) homeDownAt = event.eventTime
            KeyEvent.ACTION_UP -> {
                val held = event.eventTime - homeDownAt
                Log.d(TAG, "HOME released after ${held}ms")
                if (event.isCanceled) return true
                if (held >= LONG_PRESS_MS) {
                    showStockHome()
                } else {
                    HomeGuard.stockHomeAllowed = false
                    showCleanFrame(fromHomeKey = true)
                }
            }
        }
        return true
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        val pkg = event.packageName?.toString() ?: return
        val cls = event.className?.toString() ?: return
        // Only the home screen itself. The stock launcher package also hosts
        // the profile chooser, re-auth and install screens, and those must be
        // left alone.
        if (pkg !in HomeGuard.STOCK_LAUNCHERS || cls !in STOCK_HOME_ACTIVITIES) return
        if (HomeGuard.stockHomeAllowed) return
        Log.d(TAG, "Stock home surfaced ($cls); showing CleanFrame")
        showCleanFrame(fromHomeKey = false)
    }

    override fun onInterrupt() = Unit

    private fun showCleanFrame(fromHomeKey: Boolean) {
        val intent = Intent(this, HomeActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            .putExtra(HomeGuard.EXTRA_HOME_KEY, fromHomeKey)
        runCatching { startActivity(intent) }
            .onFailure { Log.w(TAG, "Could not show CleanFrame", it) }
    }

    private fun showStockHome() {
        HomeGuard.stockHomeAllowed = true
        for (pkg in HomeGuard.STOCK_LAUNCHERS) {
            val intent = Intent(Intent.ACTION_MAIN)
                .addCategory(Intent.CATEGORY_HOME)
                .setPackage(pkg)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            if (runCatching { startActivity(intent) }.isSuccess) return
        }
        Log.w(TAG, "No stock home screen to show")
        HomeGuard.stockHomeAllowed = false
    }

    private companion object {
        const val TAG = "CleanFrameGuard"
        const val LONG_PRESS_MS = 600L
        val STOCK_HOME_ACTIVITIES = setOf(
            "com.google.android.apps.tv.launcherx.home.HomeActivity",
            "com.google.android.apps.tv.launcherx.home.VanillaModeHomeActivity",
            "com.google.android.tvlauncher.MainActivity"
        )
    }
}

/** State shared between the service and the UI; both live in one process. */
object HomeGuard {
    const val EXTRA_HOME_KEY = "com.cleanframe.onn.extra.HOME_KEY"

    val STOCK_LAUNCHERS = setOf(
        "com.google.android.apps.tv.launcherx",
        "com.google.android.tvlauncher"
    )

    /**
     * Set when the user deliberately opens the Google TV home screen from
     * CleanFrame's own control, so the escape hatch is not immediately
     * bounced. Cleared by the next short HOME press.
     */
    @Volatile
    var stockHomeAllowed = false
}
