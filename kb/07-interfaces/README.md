# 07 — Interfaces

Externally reachable interfaces: ADB, UART, USB (including download/recovery
modes), eMMC, and any diagnostic or debug paths. How these behave — and which
functions are restricted — across generations is a recurring theme.

Record findings with `../_templates/finding.md`. Keep experiments read-only
where possible; anything that could alter device state belongs in an
`AML-E####` experiment record with an explicit `risk_level`.
