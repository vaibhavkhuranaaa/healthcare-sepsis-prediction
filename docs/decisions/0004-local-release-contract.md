# Local release contract

## Decision

Treat the repository as a local release candidate only after locked Python 3.12 checks, byte-identical synthetic evidence regeneration, public-boundary guards, container build, responsive browser evidence, current delivery graph, and release-contract validation. Keep deployment and publication statuses unapproved.

## Why

Local reproducibility, public data safety, and honest release metadata can be verified without creating cloud resources or changing GitHub. Deployment cost, public exposure, and history replacement require owner authority and external evidence.

## Alternatives rejected

Marking the project deployed was rejected because no verified HTTPS source exists. Shipping an unlocked container was rejected because it could drift from CI. Installing research dependencies in the public image was rejected because the synthetic runtime does not use them. Rewriting published history during build work was rejected because it requires a separately approved force push.

## Not done

No cloud resource was provisioned, no cost was incurred, no branch was created, no commit was made, no history was rewritten, no remote metadata was changed, and nothing was pushed or published.

## Changed

The release now has a locked cross-platform evaluation extra, corrected research dependency bounds, a minimal synthetic container, purity guards, accurate README and manifests, an MIT source license, paired responsive screenshots, and exact owner-gated next actions.
