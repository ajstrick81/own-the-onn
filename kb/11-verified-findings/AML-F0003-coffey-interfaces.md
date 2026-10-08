---
finding_id: AML-F0003
title: "coffey diagnostic / debug interface posture (read-only)"
component: interfaces
device_model: "Walmart onn 4K Plus"
soc: "Amlogic S905X5M"
generation: "S7D"
evidence_scope: exact-device
confidence: confirmed
source_refs:
  - AML-S0003
source_urls: []
source_revision: "URO4.260304.011.B1"
related_findings:
  - AML-F0001
status: promoted
---

# coffey diagnostic / debug interface posture

## Observations (device-reported, read-only)
- ADB: `init.svc.adbd = running`, `sys.usb.config = adb`,
  `persist.sys.usb.config = adb`, `service.adb.tcp.port = 5555` (adb-over-TCP
  enabled by the owner for this research).
- Security flags: `ro.secure = 1`, `ro.adb.secure = 1`, `ro.debuggable = 0`,
  `ro.force.debuggable = 0` — a locked **user** build, not debuggable.
- USB: `sys.usb.controller = fe350000.crgudc`, `init.svc.usbd = stopped`,
  `sys.usb.configfs = 2`.
- Serial **device nodes** present: `/dev/ttyS0` (crw-------, root-only) and
  `/dev/ttyS1` (crw-rw----, `bluetooth` group — HCI UART).

## Interpretation
Externally, the reachable debug surface is ADB (owner-enabled over TCP) on a
locked, non-debuggable user build. `ttyS0` is root-owned (likely the SoC debug
UART); `ttyS1` is the Bluetooth HCI link.

## Alternative explanations
`persist.sys.usb.config = adb` and the TCP port reflect the owner's research
setup, not a factory-default exposure.

## Validation needed
Per refinement #5: a `/dev/ttyS*` node is an **exposed serial device node**,
**not** a physically verified external UART header. Confirming a usable UART
(test point, pinout, console output) requires hardware probing and is out of
scope here (deferred, separate approval).
