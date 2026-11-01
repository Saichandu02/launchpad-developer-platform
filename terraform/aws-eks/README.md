# Optional AWS/EKS extension (not applied)

Networking (VPC + 2 private subnets), one narrowly scoped EKS cluster IAM role (only `AmazonEKSClusterPolicy`), private endpoint, outputs. No node group by default — add one only inside an approved spend scope.

Auth for CI: use GitHub Actions OIDC with a repository/environment-scoped IAM role trust — no permanent AWS keys (see ../../.github/workflows/ci.yml note and docs/decisions.md).

Bootstrap remote state once: create an S3 bucket + DynamoDB lock table, uncomment the backend block in main.tf, `terraform init -migrate-state`.

Use: `terraform fmt -check`, `terraform init -backend=false`, `terraform validate`, `terraform plan` (plan only with real account access; apply only within approved spending).
