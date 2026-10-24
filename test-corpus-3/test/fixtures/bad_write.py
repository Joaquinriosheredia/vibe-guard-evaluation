# Positive control: writes a file on import.
from pathlib import Path
try:
    Path("/tmp/should-not-exist").write_text("x")
except RuntimeError:
    pass
