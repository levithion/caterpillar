import os
import tempfile
from pathlib import Path

# Must be set before `app.db` (and anything importing it) is first imported,
# so tests read and write an isolated, throwaway operators database instead
# of the developer's real data/operators.db.
os.environ.setdefault("OPERATORS_DB_PATH", str(Path(tempfile.mkdtemp()) / "test_operators.db"))
