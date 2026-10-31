# Release checklist
- [ ] pytest (repo + generated service) green
- [ ] smoke_test.sh recorded in docs/verification.md
- [ ] helm lint/template on generated chart recorded
- [ ] terraform fmt/validate recorded (or noted unavailable)
- [ ] README quickstart re-run from a clean checkout
- [ ] No .env, tokens, venvs, or node_modules committed
- [ ] Tag v0.1.0 only after the above
