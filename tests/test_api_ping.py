import os
import subprocess
from app import create_app
from db.database import get_db


def setup_test_app(tmp_path):
    db_path = os.path.join(tmp_path, "test.db")
    import config

    config.Config.DATABASE = db_path
    app = create_app()
    return app


def add_device(app):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO devices (name, mac_address, ip_address, note, created_at) VALUES (?, ?, ?, ?, ?)",
            ("test", "aa:bb:cc:dd:ee:ff", "127.0.0.1", "", "now"),
        )
        db.commit()
        return db.execute("SELECT id FROM devices").fetchone()["id"]


def test_api_ping_timeout(tmp_path, monkeypatch):
    app = setup_test_app(tmp_path)
    device_id = add_device(app)

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(subprocess, "run", mock_run)

    client = app.test_client()
    resp = client.post(f"/api/ping/{device_id}")
    assert resp.status_code == 504
    assert resp.get_json() == {"success": False, "error": "Ping timed out"}
