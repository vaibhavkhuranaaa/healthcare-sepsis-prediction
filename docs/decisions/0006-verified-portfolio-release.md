# Verified portfolio release

## Decision

Enable automatic portfolio admission only when the anonymous live health route reports the exact default-branch source revision. Publish a complete v2 portfolio manifest with stakeholder copy, technical evidence, data disclosure, deployment controls, architecture, limitations, and evidence-linked resume candidates.

## Why

The portfolio should show a live system backed by the same source a reviewer can inspect. Revision verification prevents a newer repository claim from appearing beside an older deployment. A structured evidence contract keeps model metrics, threshold tradeoffs, and synthetic-only limits attached to their methods and sources.

## Alternatives rejected

Hand-editing the portfolio registry was rejected because the existing verified-release workflow already owns admission. Publishing summary copy without evidence references was rejected because it would separate strong metrics from their synthetic scope. Exposing private delivery state or local research artifacts was rejected by the public data boundary.

## Not done

No patient data, MIMIC file, trained research model, private delivery record, checksum, cost log, clinical claim, availability promise, or care recommendation was added to the portfolio contract.

## Changed

The live health response now carries deployed-source identity. Infrastructure injects that identity into the immutable revision. The release contract opts into verified admission, the portfolio manifest meets the publication schema, and a canonical architecture source describes the public and local boundaries.
