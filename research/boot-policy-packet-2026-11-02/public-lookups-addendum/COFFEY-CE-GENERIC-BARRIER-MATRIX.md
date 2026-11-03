# CoreELEC Generic boot prerequisites — S905X5M comparator matrix

Research date: 2026-11-02 (America/Chicago). This summarizes the architecture and public reports. **Every coffey-specific boot result remains U.** The matrix does not claim a successful coffey boot or compatibility with donor images/DTBs.

## Barrier matrix

| Requirement / barrier | Public evidence | What must be true for a boot | Coffey status |
|---|---|---|---|
| Correct CoreELEC generation | CoreELEC docs/forum state S905X5M support is in Amlogic-no / CoreELEC 22.0 Piers; current 22.0 Generic image is the family candidate. | Kernel and modules must support S7D; older Amlogic-ng generations are not interchangeable. | P for public build support. No coffey boot observation. |
| Board DT match | CoreELEC Generic device trees include S905X5M variants; the Xiaomi TV Box S 3rd Gen uses its own `s7d_s905x5m_xiaomi_3rd_gen.dtb`. Forum reports show SoC-generic DTB can stall on the wrong board. | Root compatible, memory, UART, clocks, regulators, storage and enabled peripherals must match the actual board. | U. Coffey vendor DT baseline is not a validated CE DTB. Do not substitute Xiaomi/Ugoos DTBs. |
| External boot entry | CoreELEC generic install documentation requires a supported boot method (recovery/app/firmware-specific trigger). Xiaomi S Box S 3rd Gen reports show “reboot to bootloader” and `adb reboot update` may reach recovery or return to Android depending on firmware/path. | Stock boot chain/recovery must actually select and load the external recovery/kernel media. Media presence alone is insufficient. | U. This is the central policy barrier. CE recovery’s own setup path writes env variables (see recovery audit). |
| Bootloader/recovery acceptance | Public reports show device- and firmware-dependent behavior. In one recent Xiaomi S Box S 3rd Gen report, a locked device with correct DTB and current firmware fell back to Android/recovery; another report later succeeded after using the board-specific route. | Image format, signature/verification policy, recovery script expectations, env state, and firmware-specific dispatch must align. | U. No inference from the S Box S 3rd Gen to coffey. |
| Storage layout and writable state | Generic image has FAT boot media plus a data partition; recovery scripts use labels, mount behavior and U-Boot environment. Exact release audited: image SHA-256 `21fc51990355adfb0f8e98df4dbd278cbb554ba346cba8e8f7c60bc4188a3eca`; nightly 2026-11-03 SHA-256 `d2af9209376120732829aab0589d7a6d3fe9c5c8dc0286a172693be1cc6775ae`. | Partitions must be discoverable under expected labels and any environment migration must complete. Recovery writes disqualify the stock installer from a read-only boundary. | U. CE recovery acceptance and environment compatibility on coffey unknown. |
| Basic kernel/hardware support | S7D vendor kernel/DT support and public CE Generic DTBs are comparators; runtime depends on correct DT and drivers. | Memory map, eMMC/USB, regulators, clocks, interrupts, UART and device-specific peripherals must initialize. | U beyond recorded baseline. A matching SoC is insufficient. |
| Video decode | S905X5M supports hardware video functions, and CE's Amlogic image includes a platform kernel/driver stack; a successful kernel boot still does not guarantee every codec path works. | Matching V4L2/media drivers, firmware, buffer allocation, color/HDR path and Kodi integration must be present and correct. | U; no coffey runtime test authorized/performed. |
| Secure media / commercial DRM | Android's certified Widevine/TEE/video path is platform-specific. A Linux boot does not by itself preserve Android secure-video services or app certification. | Separate secure decoder, TEE integration, DRM provisioning, HDCP and application support would be needed for protected services. | U for CE support on this target; no basis to promise Widevine/Netflix or equivalent. This is distinct from basic playback. |
| Usability after boot | Device tree may omit Wi-Fi/Bluetooth/remote, audio, HDMI-CEC, HDR, or suspend details even when kernel reaches userspace. | Each peripheral and media path needs a suitable driver/configuration and validation. | U. No port claim. |

## Evidence comparison: related Xiaomi device, not coffey

The CoreELEC Xiaomi Box S 3rd Gen thread identifies a different device (`MiTV-AFMU0`, codename `twilight`). Posts document the board-specific DTB, recovery/external-media paths, and firmware-sensitive fallback behavior. One 2026 owner report says a locked unit on a later firmware did not enter CoreELEC and instead returned to Android or recovery; a later post reports successful operation on another revision/path. These are useful R-class cases showing that SoC + generic image + one DTB do not settle boot behavior. They do not establish the same behavior on `darkknight` or coffey.

## Prior audited images and limits

- CoreELEC 22.0 Piers release candidate Generic image: SHA-256 `21fc51990355adfb0f8e98df4dbd278cbb554ba346cba8e8f7c60bc4188a3eca`.
- CoreELEC 22.0 Piers nightly 2026-11-03 Generic image: SHA-256 `d2af9209376120732829aab0589d7a6d3fe9c5c8dc0286a172693be1cc6775ae`.
- The extracted recovery setup path imports selected `setenv` operations into `fw_setenv`; therefore the stock recovery installer is not read-only. That finding answers the installer-side-effect question, not whether coffey accepts the image.
- The packet's donor DT comparison identifies structural differences; it does not supply a coffey-ready DTB.

## Source map

- CoreELEC Generic installation wiki: https://wiki.coreelec.org/coreelec:devgeneric
- CoreELEC DTB wiki: https://wiki.coreelec.org/coreelec:dtb
- CoreELEC boot-method wiki: https://wiki.coreelec.org/coreelec:ceboot
- CoreELEC Xiaomi TV Box S 3rd Gen thread, including firmware-sensitive report: https://discourse.coreelec.org/t/xiaomi-box-s-3rd-gen-budget-player-w-dual-boot-ce-dv-fel-google-tv/56012/540
- Follow-up successful report on that different device/firmware: https://discourse.coreelec.org/t/xiaomi-box-s-3rd-gen-budget-player-w-dual-boot-ce-dv-fel-google-tv/56012/543
- Board-specific DTB note: https://discourse.coreelec.org/t/xiaomi-box-s-3rd-gen-budget-player-w-dual-boot-ce-dv-fel-google-tv/56012/303
- CoreELEC S905X5M generic support note: https://discourse.coreelec.org/t/correct-version-for-vontar-x5-s905x5m/58252
- Existing exact-image write audit: `COFFEY-CE-RECOVERY-AUDIT.md` in the public-research packet.
- Existing donor DT comparison: `COFFEY-DTB-COMPARISON.md` in the public-research packet.

