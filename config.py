import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SQLite のファイルパス
    DATABASE = os.path.join(BASE_DIR, "wol.db")
    # Babel の初期設定
    BABEL_DEFAULT_LOCALE = "ja"
    # 将来のシークレットキー（認証機能追加時用）
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
