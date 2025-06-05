from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify
from flask_babel import Babel, _
from datetime import datetime
from config import Config
from db.database import get_db, close_db, init_db
from wake.wol import send_magic_packet
import sqlite3
import subprocess
from utils.validation import normalize_mac, InvalidMACError


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Babel(app)

    # DB 接続ライフサイクル
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        db = get_db()
        devices = db.execute("SELECT * FROM devices ORDER BY name").fetchall()
        ping_status = {}
        return render_template("devices.html", devices=devices, ping_status=ping_status)

    @app.route("/add", methods=["GET", "POST"])
    def add_device():
        if request.method == "POST":
            name = request.form["name"]
            raw_mac = request.form["mac_address"]
            try:
                mac = normalize_mac(raw_mac)
            except InvalidMACError:
                flash(_("MACアドレスの形式が不正です。"), "error")
                return render_template(
                    "device_form.html",
                    name=name,
                    mac_address=raw_mac,
                    ip_address=request.form.get("ip_address", ""),
                    note=request.form.get("note", ""),
                )

            ip = request.form.get("ip_address") or ""
            note = request.form.get("note") or ""
            now = datetime.utcnow().isoformat()
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO devices (name, mac_address, ip_address, note, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, mac, ip or None, note, now),
                )
                db.commit()
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                # UNIQUE制約違反（重複）
                flash(_("同じMACアドレスは既に登録されています。"), "error")
                # 再表示時に入力値を保持
                return render_template(
                    "device_form.html",
                    name=name,
                    mac_address=mac,
                    ip_address=ip,
                    note=note,
                )
        # GET時
        return render_template("device_form.html")

    @app.route("/api/wake/<int:device_id>", methods=["POST"])
    def api_wake(device_id):
        db = get_db()
        device = db.execute(
            "SELECT * FROM devices WHERE id = ?", (device_id,)
        ).fetchone()
        if not device:
            return jsonify(success=False, error="Device not found"), 404
        try:
            send_magic_packet(device["mac_address"])
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/delete/<int:device_id>", methods=["POST"])
    def api_delete(device_id):
        db = get_db()
        res = db.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        db.commit()
        if res.rowcount:
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Device not found"), 404

    @app.route("/api/ping/<int:device_id>", methods=["POST"])
    def api_ping(device_id):
        db = get_db()
        device = db.execute(
            "SELECT * FROM devices WHERE id = ?", (device_id,)
        ).fetchone()
        if not device or not device["ip_address"]:
            return jsonify(success=False, error="IP address missing"), 400
        try:
            proc = subprocess.run(
                ["ping", "-c", "1", device["ip_address"]],
                stdout=subprocess.DEVNULL,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            return jsonify(success=False, error="Ping timed out"), 504

        status = "online" if proc.returncode == 0 else "offline"
        return jsonify(success=True, status=status)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
