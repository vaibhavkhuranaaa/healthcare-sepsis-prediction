# Dashboard evidence hierarchy

## Decision

Keep the existing dependency-free Flask and native web stack, and reshape the dashboard around synthetic probability context, an illustrative threshold control, a responsive timeline, evidence boundaries, contributor limits, and explicit loading, empty, and connection-error states.

## Why

The reviewer needs to understand what changes with threshold choice and what the public demo cannot establish. A native range control and accessible SVG make that consequence visible without adding a frontend framework or chart dependency.

## Alternatives rejected

A React rewrite was rejected because the page has one route and no state complexity that justifies a build system. A circular risk gauge was rejected because it over-emphasized one score and resembled an alarm. A static report was rejected because it could not show threshold consequences or recovery states.

## Not done

No care action, recommended threshold, diagnosis, treatment, patient workflow, real-time feed, or clinical claim was added. No external font, icon, analytics, or chart service was introduced.

## Changed

The dashboard now provides stakeholder hierarchy, native threshold interaction, above-threshold window counts, semantic live status, retry behavior, accessible chart descriptions and table data, reduced-motion support, and single-column mobile composition.
