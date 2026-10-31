"""LaunchPad local scaffolder: one golden path (Python FastAPI).

Local mode needs no GitHub token. Connected mode (publishing to GitHub /
GHCR / Argo CD) is configuration documented in docs/, not executed here.
Rollback is a *git revert* commit in the GitOps folder, so Argo CD
reconciles the reverted state instead of fighting a manual kubectl undo.
"""
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{2,30}[a-z0-9]$")
OWNER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
ENVS = {"dev", "staging", "prod"}
BAD = ("..", "/", "\\", "\x00", "${", "{{", "}}", ";", "`", "$(", "\n", "\r", "'", '"', "<", ">", "|", "&")

def validate(name, description, owner, environment):
    errors = []
    if not NAME_RE.match(name or ""):
        errors.append("name must be 4-32 chars, start with a letter, contain only lowercase letters, digits, hyphens, and not end with a hyphen")
    if any(b in (name or "") for b in BAD): errors.append("name contains forbidden characters / path traversal")
    if environment not in ENVS: errors.append(f"environment must be one of {sorted(ENVS)}")
    if not OWNER_RE.match(owner or ""): errors.append("owner must be a simple user/team slug (letters, digits, hyphens)")
    if not description or len(description) > 140 or any(b in description for b in BAD):
        errors.append("description must be 1-140 chars with no template/path/shell metacharacters")
    return errors

def render(src: Path, dst: Path, values: dict):
    if dst.exists() and any(dst.iterdir()):
        raise SystemExit(f"output folder already exists and is not empty: {dst}")
    dst.mkdir(parents=True, exist_ok=True)
    tpl_root = Path(__file__).resolve().parent.parent / "templates" / "service"
    count = 0
    for f in sorted(tpl_root.rglob("*")):
        if f.is_dir() or "__pycache__" in f.parts: continue
        rel = f.relative_to(tpl_root)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        text = f.read_text()
        for k, v in values.items(): text = text.replace(k, v)
        if any(k in text for k in values):
            raise SystemExit(f"unrendered placeholder left in {rel}")
        out.write_text(text); count += 1
    return count

def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.name=LaunchPad", "-c", "user.email=launchpad@example.invalid", *args],
                          cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()

def gitops_write(gitops: Path, name, version, environment, image):
    d = gitops / name; d.mkdir(parents=True, exist_ok=True)
    (d / "values.yaml").write_text(
        f"image:\n  repository: {image}\n  tag: \"{version}\"\nreplicaCount: 1\n"
        f"service:\n  name: {name}\n  environment: {environment}\n")
    (d / "kustomization-note.md").write_text(
        f"# GitOps state for {name}\nArgo CD watches this folder. Change = git commit. Rollback = git revert (see launchpad rollback).\n")
    if not (gitops / ".git").exists():
        git("init", "-q", cwd=gitops); git("add", "-A", cwd=gitops); git("commit", "-qm", f"gitops: add {name} {version}", cwd=gitops)
    else:
        git("add", "-A", cwd=gitops)
        if git("status", "--porcelain", cwd=gitops):
            git("commit", "-qm", f"gitops: {name} -> {version}", cwd=gitops)
    return git("rev-parse", "--short", "HEAD", cwd=gitops)

def cmd_create(a):
    errs = validate(a.name, a.description, a.owner, a.environment)
    if errs:
        for e in errs: print(f"ERROR: {e}", file=sys.stderr)
        return 2
    values = {"__SERVICE_NAME__": a.name, "__SERVICE_TITLE__": a.name.replace("-", " ").title(),
              "__SERVICE_DESCRIPTION__": a.description, "__OWNER__": a.owner,
              "__ENVIRONMENT__": a.environment, "__VERSION__": "0.1.0"}
    t0 = time.perf_counter()
    n = render(Path(__file__), Path(a.output), values)
    secs = round(time.perf_counter() - t0, 3)
    result = {"service": a.name, "output": str(Path(a.output).resolve()), "files_rendered": n, "render_seconds": secs}
    if a.gitops_dir:
        commit = gitops_write(Path(a.gitops_dir), a.name, "0.1.0", a.environment, f"ghcr.io/example/{a.name}")
        result["gitops_commit"] = commit
    print(json.dumps(result, indent=2)); return 0

def cmd_update(a):
    if not VERSION_RE.match(a.version): print("ERROR: version must be x.y.z", file=sys.stderr); return 2
    g = Path(a.gitops_dir); vf = g / a.name / "values.yaml"
    if not vf.exists(): print(f"ERROR: no gitops state for {a.name}", file=sys.stderr); return 2
    text = re.sub(r'tag: "[^"]+"', f'tag: "{a.version}"', vf.read_text()); vf.write_text(text)
    git("add", "-A", cwd=g); git("commit", "-qm", f"gitops: {a.name} -> {a.version}", cwd=g)
    print(json.dumps({"service": a.name, "version": a.version, "commit": git("rev-parse", "--short", "HEAD", cwd=g)})); return 0

def cmd_rollback(a):
    """Rollback that persists in Git: revert the latest GitOps commit for the service.
    Argo CD then reconciles the reverted (previous) desired state."""
    g = Path(a.gitops_dir)
    if not (g / ".git").exists(): print("ERROR: gitops folder is not a git repo", file=sys.stderr); return 2
    git("revert", "--no-edit", "HEAD", cwd=g)
    vf = (g / a.name / "values.yaml").read_text()
    print(json.dumps({"service": a.name, "rolled_back_to_values": vf, "commit": git("rev-parse", "--short", "HEAD", cwd=g)})); return 0

def main(argv=None):
    p = argparse.ArgumentParser(prog="launchpad"); sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create"); c.add_argument("--name", required=True); c.add_argument("--description", required=True)
    c.add_argument("--owner", required=True); c.add_argument("--environment", default="dev")
    c.add_argument("--output", required=True); c.add_argument("--gitops-dir"); c.set_defaults(fn=cmd_create)
    u = sub.add_parser("update"); u.add_argument("--name", required=True); u.add_argument("--version", required=True); u.add_argument("--gitops-dir", required=True); u.set_defaults(fn=cmd_update)
    r = sub.add_parser("rollback"); r.add_argument("--name", required=True); r.add_argument("--gitops-dir", required=True); r.set_defaults(fn=cmd_rollback)
    a = p.parse_args(argv); return a.fn(a)

if __name__ == "__main__": raise SystemExit(main())
