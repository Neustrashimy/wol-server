# tests/conftest.py
import sys
import os

# tests/ の一つ上のディレクトリ（プロジェクトルート）を sys.path に追加
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
