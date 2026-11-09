package com.cleanframe.onn

import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.Drawable
import android.webkit.WebResourceResponse
import androidx.webkit.WebViewAssetLoader
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream

/**
 * Serves installed-app artwork to the WebView as real image responses.
 *
 * Upstream reads `a.iconPath` from Tizen, which is a file path the TV's web
 * runtime can load directly. Android has no such path: artwork comes out of
 * PackageManager as a Drawable. Rather than base64 a dozen PNGs into the apps
 * payload, this handler answers `/icon/<package>.png` on the same virtual
 * origin as the rest of the assets, so the browser caches them normally.
 *
 * Banner is preferred over icon, since Android TV banners are the 16:9 artwork
 * built for a ten-foot UI and match CleanFrame's dock proportions.
 */
class IconPathHandler(private val context: Context) : WebViewAssetLoader.PathHandler {

    private val cache = HashMap<String, ByteArray>()

    override fun handle(path: String): WebResourceResponse? {
        val pkg = path.removeSuffix(".png").trim('/')
        if (pkg.isEmpty()) return null

        val png = synchronized(cache) { cache[pkg] } ?: run {
            val bytes = render(pkg) ?: return null
            synchronized(cache) { cache[pkg] = bytes }
            bytes
        }

        return WebResourceResponse("image/png", null, ByteArrayInputStream(png)).apply {
            responseHeaders = mapOf("Cache-Control" to "max-age=3600")
        }
    }

    private fun render(pkg: String): ByteArray? {
        val pm = context.packageManager
        val drawable: Drawable = runCatching { pm.getApplicationBanner(pkg) }.getOrNull()
            ?: runCatching { pm.getApplicationIcon(pkg) }.getOrNull()
            ?: return null

        val bitmap = drawable.toBitmap() ?: return null
        val out = ByteArrayOutputStream()
        return if (bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)) out.toByteArray() else null
    }

    /**
     * Adaptive and vector drawables report no bitmap of their own, so they are
     * drawn onto a canvas at their intrinsic size (falling back to a square
     * when they declare none).
     */
    private fun Drawable.toBitmap(): Bitmap? {
        if (this is BitmapDrawable) bitmap?.let { return it }

        val width = if (intrinsicWidth > 0) intrinsicWidth else FALLBACK_SIZE
        val height = if (intrinsicHeight > 0) intrinsicHeight else FALLBACK_SIZE
        return runCatching {
            Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888).also { bmp ->
                val canvas = Canvas(bmp)
                setBounds(0, 0, canvas.width, canvas.height)
                draw(canvas)
            }
        }.getOrNull()
    }

    private companion object {
        /** Android TV banners are 320x180; a square fallback covers plain icons. */
        const val FALLBACK_SIZE = 180
    }
}
