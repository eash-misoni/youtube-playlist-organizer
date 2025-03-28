import os
import sys

# バックエンドディレクトリをPythonパスに追加
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir) 