from worktree_manager.templating import slug, db, port_hash, render


def test_filters_and_dotted_rendering():
    values = {"task": "Fix Example!", "resources": {"ports": {"app": 8123}}}
    assert slug("Fix Example!") == "fix-example"
    assert db("Fix-Example!") == "fix_example"
    assert 8001 <= port_hash("abc", 8001, 8003) <= 8003
    assert render("${task|slug}:${resources.ports.app}", values) == "fix-example:8123"
