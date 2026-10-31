# Architecture

```text
Developer
  |  form (Backstage Software Template: backstage/templates/python-fastapi/template.yaml)
  |  or CLI (python3 scaffold.py create ...)
  v
Scaffolder (launchpad/scaffold.py) --validate--> reject traversal/injection/bad env
  |  render templates/service/ (token substitution, leftover-token check)
  v
Generated service (FastAPI)  /healthz /readyz /metrics /api/info, tests, Dockerfile
  |  connected mode: GitHub repo + GitHub Actions -> GHCR image (immutable tag/digest)
  v
GitOps folder (gitops/<service>/values.yaml, git-committed)
  |  Argo CD Application (gitops/argocd-application.yaml) syncs Helm chart
  v
Cluster: kind locally / EKS via terraform/aws-eks (optional) -- Helm: probes,
resource requests/limits, runAsNonRoot, dedicated ServiceAccount
```

Components: Backstage catalog (`backstage/catalog-info.yaml`, `app-config.yaml` with PostgreSQL) holds the System + template Location; the generated service registers itself via its rendered `catalog-info.yaml`. Separation: the *service repo* holds code; the *GitOps folder/repo* holds desired deployment state — image-tag changes never touch service code, which is what makes revert-based rollback clean.
