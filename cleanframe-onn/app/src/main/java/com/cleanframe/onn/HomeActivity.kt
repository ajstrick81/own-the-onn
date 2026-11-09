package com.cleanframe.onn

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.webkit.ConsoleMessage
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader

/**
 * Hosts CleanFrame's web UI as the device home screen.
 *
 * Assets are served over the virtual https origin `appassets.androidplatform.net`
 * rather than `file://`. That matters for more than tidiness: CleanFrame persists
 * its preferences in `localStorage` (main.js:321-378), and Web Storage on a
 * `file://` document is unreliable and partly disabled on modern WebView. A real
 * secure origin gives it a stable, durable storage partition.
 */
class HomeActivity : AppCompatActivity() {

    private lateinit var web: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val loader = WebViewAssetLoader.Builder()
            .setDomain(ASSET_DOMAIN)
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .addPathHandler("/icon/", IconPathHandler(this))
            .build()

        web = WebView(this).apply {
            setBackgroundColor(android.graphics.Color.BLACK)

            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            settings.mediaPlaybackRequiresUserGesture = false
            // Everything is local; no plaintext or cross-origin loads needed.
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.cacheMode = android.webkit.WebSettings.LOAD_DEFAULT

            // CleanFrame drives focus itself via its own key handler, so the
            // WebView's native focus ring would fight it for the D-pad.
            isFocusable = true
            isFocusableInTouchMode = true
            overScrollMode = View.OVER_SCROLL_NEVER
            isHorizontalScrollBarEnabled = false
            isVerticalScrollBarEnabled = false

            addJavascriptInterface(DeviceBridge(this@HomeActivity), BRIDGE_NAME)

            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? = loader.shouldInterceptRequest(request.url)

                /**
                 * A home screen must never become a browser. Any navigation
                 * away from the local origin is refused outright.
                 */
                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean = request.url.host != ASSET_DOMAIN
            }

            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    android.util.Log.d(
                        TAG,
                        "${message.sourceId()}:${message.lineNumber()} ${message.message()}"
                    )
                    return true
                }
            }
        }

        setContentView(web)
        hideSystemBars()
        web.loadUrl("https://$ASSET_DOMAIN/assets/web/index.html")
        web.requestFocus()
    }

    /**
     * Translate the remote's BACK into the keyCode 27 that CleanFrame's key map
     * already understands (main.js:13), instead of letting Android finish the
     * Activity. A home screen has nowhere to go back to, so BACK must stay
     * inside the UI; `__cleanframeBack()` returns false only at the top level,
     * where the press is then correctly ignored.
     */
    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            web.evaluateJavascript("window.__cleanframeBack && window.__cleanframeBack()", null)
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    /** Swallow BACK's default Activity-finishing behaviour as well. */
    @Deprecated("Required while the Activity still handles BACK directly.")
    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        // Intentionally empty: BACK is delivered to the web UI in onKeyDown.
    }

    /**
     * The HOME key is delivered to whichever app is the active home screen.
     * When CleanFrame is already showing, re-press should settle it back to
     * the top level rather than reload it.
     */
    override fun onNewIntent(intent: android.content.Intent?) {
        super.onNewIntent(intent)
        web.evaluateJavascript("window.__cleanframeHome && window.__cleanframeHome()", null)
    }

    override fun onResume() {
        super.onResume()
        hideSystemBars()
        web.onResume()
        web.requestFocus()
    }

    override fun onPause() {
        web.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    @Suppress("DEPRECATION")
    private fun hideSystemBars() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.setDecorFitsSystemWindows(false)
            window.insetsController?.hide(android.view.WindowInsets.Type.systemBars())
        } else {
            window.decorView.systemUiVisibility =
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
                    View.SYSTEM_UI_FLAG_FULLSCREEN or
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        }
    }

    private companion object {
        const val TAG = "CleanFrameHome"
        const val ASSET_DOMAIN = "appassets.androidplatform.net"
        const val BRIDGE_NAME = "CleanFrameNative"
    }
}
