/* Google TV / Android TV implementation of CleanFrame's platform seam.
 *
 * Drop-in replacement for upstream app/device.js (which targets Tizen). It
 * exposes exactly the same nine methods on window.FrameDevice, with the same
 * done(err, value) callback contract and the same error-object shape
 * ({ message, detail }), so app/main.js runs unmodified.
 *
 * Backed by the CleanFrameNative JS bridge in DeviceBridge.kt. Kept in ES5 to
 * match upstream's runtime target.
 *
 * tools/sync-upstream.sh copies this file over web/device.js at build time.
 */
(function () {
  'use strict';

  // ------------------------------------------------------------- viewport fix

  /* CleanFrame's stage is absolutely positioned at a fixed 1920x1080 (it was
     built for a 1080p Samsung panel). Upstream's meta is
     "width=device-width, initial-scale=1", which on Tizen yields a 1920 CSS px
     viewport because the TV reports density 1.

     coffey reports density 2, so device-width is 960 CSS px: the layout
     viewport becomes 960x540 and only the stage's top-left quadrant is on
     screen. The clock (at y=72) shows, the dock (at y=692) is below the fold,
     and the UI looks like a bare wallpaper with a clock.

     Pinning the viewport to the stage's own 1920x1080 makes the layout
     density-independent; the browser then scales it to fit the window, which
     on a 1080p screen at density 2 lands on exact native pixels. This runs
     before main.js, so its first measurement already sees the right size. */
  (function fixViewport() {
    var meta = document.querySelector('meta[name=viewport]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'viewport');
      document.head.appendChild(meta);
    }
    var wanted = 'width=1920, height=1080, user-scalable=no';
    if (meta.getAttribute('content') !== wanted) meta.setAttribute('content', wanted);
  }());

  function native() {
    return window.CleanFrameNative || null;
  }

  /* Mirrors upstream's message when the UI runs outside the device. */
  function unavailable(done) {
    done({
      message: 'Open CleanFrame on the TV to use this control.',
      detail: 'The web preview cannot control the device.'
    });
  }

  /* The bridge returns '' for success, or a JSON error object as a string. */
  function settle(raw, done, value) {
    if (raw === '' || raw === null || raw === undefined) {
      done(null, value);
      return;
    }
    var err;
    try {
      err = JSON.parse(raw);
    } catch (e) {
      err = { message: 'The device could not open this screen.' };
    }
    done(err);
  }

  /* Bridge calls are synchronous, but callers expect an async callback, so
     results are delivered on a later tick to keep call ordering predictable. */
  function later(fn) {
    setTimeout(fn, 0);
  }

  function guard(call, done) {
    var api = native();
    if (!api) {
      unavailable(done);
      return;
    }
    var raw;
    try {
      raw = call(api);
    } catch (err) {
      later(function () {
        done({
          message: 'The device could not open this screen.',
          detail: (err && (err.message || err.name)) || 'Try again.'
        });
      });
      return;
    }
    later(function () {
      settle(raw, done);
    });
  }

  // ------------------------------------------------------------------ launching

  function launchApp(id, done) {
    guard(function (api) {
      return api.launchPackage(String(id || ''));
    }, done);
  }

  function launch(brand, done) {
    guard(function (api) {
      return api.launchBrand(String(brand || ''));
    }, done);
  }

  /* Upstream opens the Samsung home screen; here it is the Google TV launcher
     this app replaces, which stays reachable as an explicit escape hatch. */
  function home(done) {
    guard(function (api) {
      return api.openSystemHome();
    }, done);
  }

  function settings(done) {
    guard(function (api) {
      return api.openSettings();
    }, done);
  }

  /* No Art Mode exists on a streamer. The nearest real destination is the
     ambient/screensaver setting; the bridge reports plainly if even that is
     absent, rather than faking a mode the hardware does not have. */
  function art(done) {
    guard(function (api) {
      return api.openAmbient();
    }, done);
  }

  // ------------------------------------------------------------------ discovery

  function apps(done) {
    var api = native();
    if (!api) {
      unavailable(done);
      return;
    }
    var list;
    try {
      list = JSON.parse(api.listApps() || '[]');
    } catch (err) {
      later(function () {
        done({ message: 'The device could not list its apps.' });
      });
      return;
    }
    later(function () {
      done(null, list);
    });
  }

  // --------------------------------------------------------------------- inputs

  /* The Onn 4K Plus is an HDMI source with no inputs of its own, so the list is
     always empty and CleanFrame hides the inputs row. Reported as an empty
     success rather than an error: there is nothing wrong, there is just nothing
     to switch to. */
  function sources(done) {
    var api = native();
    var list = [];
    if (api) {
      try {
        list = JSON.parse(api.listSources() || '[]');
      } catch (err) {
        list = [];
      }
    }
    later(function () {
      done(null, list);
    });
  }

  function setSource(port, done) {
    later(function () {
      done({
        message: 'This device has no HDMI inputs.',
        detail: 'The Onn streamer is an HDMI source, not a TV with inputs.'
      });
    });
  }

  function cancelSource() {
    /* Nothing to cancel: there is no pending input switch on this platform. */
  }

  // --------------------------------------------------------- first-run seeding

  /* Upstream's nine default Home slots are Samsung brand ids (main.js:16-25).
     On Tizen those always resolve, because the TV ships those apps. On Google
     TV none of them need exist, so an unseeded first run draws an empty dock.

     This runs before main.js and, only when nothing has been saved yet, writes
     a config whose Home list is built from what is actually installed. After
     that the user's own saved config is authoritative and this never runs
     again -- it seeds, it does not override.

     Schema per main.js clean()/serialise(): appRecords supplies names and
     icons for non-brand apps, home is the ordered id list, CAP is 9. */
  var STORAGE_KEY = 'cleanframe.home.v1';
  var LEGACY_KEY = 'cleanframe.shore.v1';
  var HOME_CAP = 9;

  /* Brand ids main.js already knows; these must stay as brand ids so its own
     catalog refresh can attach the real package to them. */
  var PRIMARY_BRANDS = ['stremio', 'netflix', 'disneyplus', 'youtube', 'appletv',
    'primevideo', 'abciview', 'sbs', 'applemusic'];

  function alreadySeeded() {
    try {
      return !!(localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_KEY));
    } catch (err) {
      /* Storage unavailable: main.js reports that itself; do not seed. */
      return true;
    }
  }

  function seedFromInstalledApps() {
    var api = native();
    if (!api || alreadySeeded()) return;

    var entries;
    try {
      entries = JSON.parse(api.listApps() || '[]');
    } catch (err) {
      return;
    }
    if (!entries.length) return;

    var home = [], records = [], i, entry, id, isBrand;
    for (i = 0; i < entries.length && home.length < HOME_CAP; i++) {
      entry = entries[i];
      if (!entry || !entry.appId || !entry.name) continue;

      isBrand = entry.brand && PRIMARY_BRANDS.indexOf(entry.brand) >= 0;
      id = isBrand ? entry.brand : entry.appId;
      if (home.indexOf(id) >= 0) continue;
      home.push(id);

      /* Brand slots already exist in main.js's APPS table with a proper name,
         so a record would be ignored; only non-brand apps need one. */
      if (!isBrand) {
        records.push({
          id: id,
          appId: entry.appId,
          name: String(entry.name).slice(0, 160),
          brand: '',
          icon: entry.icon || ''
        });
      }
    }
    if (!home.length) return;

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        version: 2,
        home: home,
        dock: home.slice(),
        recent: [],
        lastApp: home[0],
        appRecords: records
      }));
    } catch (err) {
      /* Nothing to do: main.js falls back to its own defaults. */
    }
  }

  seedFromInstalledApps();

  window.FrameDevice = {
    launch: launch,
    launchApp: launchApp,
    art: art,
    home: home,
    settings: settings,
    apps: apps,
    sources: sources,
    setSource: setSource,
    cancelSource: cancelSource
  };

  // ------------------------------------------------------- remote key delivery

  /* main.js reads ev.keyCode on document keydown (main.js:13 key map). Android
     delivers BACK and HOME to the Activity, not to the WebView, so HomeActivity
     calls these hooks and they re-enter the UI as the key codes it expects.
     A matching keyup is required: main.js debounces held BACK via heldKeys, and
     without the release the next press would be swallowed. */
  function tap(keyCode) {
    ['keydown', 'keyup'].forEach(function (type) {
      var ev;
      try {
        ev = new Event(type, { bubbles: true, cancelable: true });
      } catch (err) {
        ev = document.createEvent('Event');
        ev.initEvent(type, true, true);
      }
      ev.keyCode = keyCode;
      ev.which = keyCode;
      document.dispatchEvent(ev);
    });
  }

  /* BACK -> keyCode 27. Returns true so the Activity knows it was handled. */
  window.__cleanframeBack = function () {
    tap(27);
    return true;
  };

  /* HOME pressed while CleanFrame is already foreground: step up one level,
     which settles an open sheet or detail view back toward the home stage. */
  window.__cleanframeHome = function () {
    tap(27);
    return true;
  };
}());
