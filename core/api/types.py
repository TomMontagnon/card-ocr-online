from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict

Frame = np.ndarray  # BGR uint8 par convention

@dataclass
class Meta:
    ts_ms: int
    info: Dict[str, Any] | None = None
