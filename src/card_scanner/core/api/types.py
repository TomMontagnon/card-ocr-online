from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

Frame = np.ndarray  # BGR uint8 par convention

@dataclass
class Meta:
    ts_ms: int = 0
    info: dict[str, Any] = field(default_factory=dict)
    state_OK : bool = True


class Database(Enum):
    SWUDB = "swudb.com (.csv)"
    DATABASE2 = "database2 (.csv)"

class Expansion(Enum):
    SOR_EN = 2
    SOR_DE = 3
    SOR_FR = 4
    SOR_ES = 5
    SOR_IT = 6
    SHD_EN = 8
    SHD_DE = 9
    SHD_FR = 10
    SHD_ES = 11
    SHD_IT = 12
    C24_EN = 13
    C24_DE = 14
    C24_FR = 15
    C24_ES = 16
    C24_IT = 17
    TWI_EN = 18
    TWI_DE = 19
    TWI_FR = 20
    TWI_ES = 21
    TWI_IT = 22
    JTL_EN = 23
    JTL_DE = 24
    JTL_ES = 25
    JTL_IT = 26
    JTL_FR = 27
    J24_EN = 28
    J24_DE = 29
    J24_FR = 30
    J24_ES = 31
    J24_IT = 32
    J25_EN = 33
    J25_DE = 34
    J25_FR = 35
    J25_ES = 36
    J25_IT = 37
    P25_EN = 38
    P25_DE = 39
    P25_FR = 40
    P25_ES = 41
    P25_IT = 42
    GG_EN = 43
    GG_DE = 44
    GG_FR = 45
    GG_ES = 46
    GG_IT = 47
    JTLW_EN = 48
    JTLW_DE = 49
    JTLW_FR = 50
    JTLW_ES = 51
    JTLW_IT = 52
    LOF_EN = 53
    LOF_DE = 54
    LOF_FR = 55
    LOF_ES = 56
    LOF_IT = 57
    LOFW_EN = 58
    LOFW_DE = 59
    LOFW_FR = 60
    LOFW_ES = 61
    LOFW_IT = 62
    C25_EN = 63
    C25_DE = 64
    C25_FR = 65
    C25_ES = 66
    C25_IT = 67
    IBH_EN = 68
    IBH_DE = 69
    IBH_FR = 70
    IBH_ES = 71
    IBH_IT = 72
    SEC_EN = 73
    SEC_DE = 74
    SEC_FR = 75
    SEC_ES = 76
    SEC_IT = 77


class NoCardDetectedError(Exception):
    pass

class NoSourceAvailableError(Exception):
    pass
