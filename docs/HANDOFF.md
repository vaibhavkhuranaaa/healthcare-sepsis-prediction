# Handoff

Release automation is intentionally `planned` in `portfolio/release.json`. Do not deploy or publish until calibration evidence, clinical limitations, and any Azure cost boundary are explicitly approved.

Read `AGENTS.md`, `README.md`, `docs/STATE.md`, and fresh Graphify output before work.

Next action: verify the synthetic path independently of restricted local research, run the repository checks, and create versioned calibration/data-boundary evidence before advancing the manifest. Preserve all existing dirty work and do not invent clinical or deployment claims.

Rollback the stabilization only through a reviewed `git revert 5605582b9e20ac514ea921e32854ee1ae34bb966`; do not reset to `f81f678d92c4746e4622d40756a470481af26469`.
