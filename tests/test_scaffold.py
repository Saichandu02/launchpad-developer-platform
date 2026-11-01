
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from launchpad.scaffold import validate, main

def test_valid(): assert validate("demo-orders", "Demo orders service", "team-a", "dev") == []
def test_traversal(): assert validate("../etc-passwd", "x", "team-a", "dev")
def test_uppercase_and_underscore(): assert validate("Demo_Orders", "x", "team-a", "dev")
def test_injection_description(): assert validate("demo-orders", "x ${{ evil }}", "team-a", "dev")
def test_bad_env(): assert validate("demo-orders", "x", "team-a", "production;rm")
def test_create_and_gitops_rollback(tmp_path):
    out, gops = tmp_path/"svc", tmp_path/"gitops"
    assert main(["create","--name","demo-orders","--description","Demo orders service","--owner","team-a","--environment","dev","--output",str(out),"--gitops-dir",str(gops)]) == 0
    assert (out/"app/main.py").exists() and "demo-orders" in (out/"catalog-info.yaml").read_text()
    assert main(["update","--name","demo-orders","--version","0.2.0","--gitops-dir",str(gops)]) == 0
    assert 'tag: "0.2.0"' in (gops/"demo-orders/values.yaml").read_text()
    assert main(["rollback","--name","demo-orders","--gitops-dir",str(gops)]) == 0
    assert 'tag: "0.1.0"' in (gops/"demo-orders/values.yaml").read_text()  # revert persisted in git
