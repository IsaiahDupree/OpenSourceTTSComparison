
import os
from pathlib import Path

# Create the TOS accepted marker file manually
tos_marker = Path.home() / ".local" / "share" / "tts" / "xtts_v2_tos_accepted"
tos_marker.parent.mkdir(parents=True, exist_ok=True)
tos_marker.touch()
print(f"Created TOS marker at: {tos_marker}")

# Also set env var just in case
os.environ["COQUI_TOS_AGREED"] = "1"
print("Set COQUI_TOS_AGREED=1")
