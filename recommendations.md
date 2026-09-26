# Recommendations (DRAFT)

Ranked by effort versus payoff. **Settings first**; DNS rules and patches are separate, opt-in follow-ups.

## Settings you can change now (no tools)

1. **Keep your TV offline** if the onn does all the streaming. That's the single strongest protection against TV-side ACR.
2. **Google TV:** Settings → Privacy → **Usage & diagnostics** → off; **Ads** → delete / reset advertising ID and opt out
   of personalization. *(Verify exact menu names on your firmware.)*
3. **Uninstall or disable apps you don't use.** In our capture, unopened apps (Twitch, NordVPN, ESPN, Tubi and others) sent
   analytics while the device was idle and asleep.
4. **Preinstalled Netflix:** if you don't use it, disable it (Settings → Apps → Netflix → Disable). It kept logging
   while the screen was off.
5. **Screen-off doesn't mean offline.** The onn keeps its network up while asleep. Unplug it if you want it truly silent.

## Host TV

- **Samsung 2016–2018 (Tizen):** Settings → Support → Terms & Policy → turn off **Viewing Information Services**,
  **Interest-Based Advertisement** and **Voice Recognition Services**.
- **Samsung 2013–2014 (Orsay):** Smart Hub → Terms & Policy → turn off **SyncPlus and Marketing** and **Interactive Service**.
- **LG:** Live Plus / Viewing Information. **Vizio:** Viewing Data. **Roku TV:** "Use info from TV inputs".
  **Sony / TCL / Hisense Google TV:** Samba TV (if present) and Usage & diagnostics.
- If the TV must stay online, forget any Wi-Fi it doesn't need and add it to your DNS filtering.

## DNS rules (for discussion)

- Candidate blocks: third-party analytics hosts observed while idle. See `blocklists/` *(pending)*.
- **Caveat:** some apps bypass system DNS (the Netflix client queried `8.8.8.8` directly), so router-level DNS
  alone won't catch everything.

## Patch-level (for discussion, not implemented)

- Per-app analytics removal, as in the Tubi pilot in morphe-androidtv-patches.
