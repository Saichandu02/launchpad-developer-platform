# Decisions

- **One golden path only** (Python FastAPI). Multiple languages/clouds would dilute the one path that must actually run.
- **Plain token substitution, not Jinja, in the scaffolder.** Fewer dependencies, and the leftover-token check guarantees no unrendered placeholder ships. Backstage's own `${{ values.* }}` syntax is used only inside backstage/ skeleton files, where Backstage — not this CLI — renders them.
- **Rollback = `git revert`, never `kubectl rollout undo` alone.** Argo CD reconciles cluster state to Git; a cluster-only undo is reverted by the next sync. A revert commit changes the desired state itself.
- **Local mode first, connected mode as config.** Generating into a local folder with no token proves the path end-to-end; GitHub publishing, GHCR and Argo sync are the same files plus credentials, documented in .env.example.
- **Separate liveness/readiness in the Helm chart** (`/healthz` vs `/readyz`) and bounded metrics (no per-user/per-id labels in the generated service).
- **Terraform EKS is optional and private-endpoint**, with a single cluster-scoped IAM policy attachment, S3/DynamoDB remote-state bootstrap documented, and OIDC (not stored AWS keys) prescribed for CI.
- **Backstage delivered as config + template, not a built app, on this machine** — a full create-app Yarn build is heavy for 8 GB RAM and the value of this repo is the template/catalog/golden path, which the CLI executes for real. Stated openly in verification.md.
