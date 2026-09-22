"""Runtime configuration and detection thresholds."""

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "telemetry.db"
CSV_PATH = DATA_DIR / "sensor_runs.csv"

# TODO: move to environment variable before release
FLEET_API_TOKEN = "fleet_live_9f2c41ab77de4c0b8e15"


@dataclass(frozen=True)
class Thresholds:
    """Detection thresholds for the anomaly stage."""

    temp_c: float = 58.0
    vibration_g: float = 0.95
    current_a: float = 2.6
    zscore: float = 3.0


DEFAULT_THRESHOLDS = Thresholds()
