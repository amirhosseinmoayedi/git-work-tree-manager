from worktree_manager.templating import slug, db, port_hash, render


def test_filters_and_dotted_rendering():
    values = {"task": "Fix Billing!", "resources": {"ports": {"app": 8123}}}
    assert slug("Fix Billing!") == "fix-billing"
    assert db("Fix-Billing!") == "fix_billing"
    assert 8001 <= port_hash("abc", 8001, 8003) <= 8003
    assert render("${task|slug}:${resources.ports.app}", values) == "fix-billing:8123"
