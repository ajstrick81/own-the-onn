---
experiment_id: AML-E9001
title: "[ILLUSTRATIVE EXAMPLE] Read-only UART presence check"
research_question: "Does the board expose a populated, active UART test point at boot?"
hypothesis: "A serial console is present and prints BL/U-Boot logs at a standard baud."
target_device: "[example only — not a real run]"
risk_level: read-only
prerequisites:
  - "USB-TTL adapter (3.3V)"
  - "Non-destructive probing only"
result: not-started
artifacts: []
related_findings: []
---

# AML-E9001 — [ILLUSTRATIVE EXAMPLE] Read-only UART presence check

> **This is a clearly-labeled example record** showing the experiment format.
> The `9xxx` id range is reserved for illustrative/example records so they
> never collide with real numbering. Delete or ignore when copying.

## Procedure
1. Identify candidate test points visually (no desolder).
2. Probe for a TX line that idles high and emits data at power-on.
3. Attach RX-only first; sweep common baud rates read-only.

## Expected observations
- A readable boot log ⇒ active console present (record baud).
- Idle-high but silent ⇒ possibly TX-disabled in production.
- Nothing ⇒ not a UART, or not populated.

## Actual observations
<none — example>

## Conclusion
<none — example>

## Next steps
<none — example>
