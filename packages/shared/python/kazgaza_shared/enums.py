"""Enums shared between the backend API and the Telegram bot.

Kept as a single source of truth so both services agree on the same
wire values for application lifecycle fields.
"""
from enum import Enum


class ApplicationType(str, Enum):
    METER_NOT_WORKING = "METER_NOT_WORKING"
    MPI_REMOVAL = "MPI_REMOVAL"
    GAS_LEAK = "GAS_LEAK"


class ApplicationStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class ApplicationPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FileType(str, Enum):
    METER_PHOTO = "METER_PHOTO"
    GAS_LEAK_PHOTO = "GAS_LEAK_PHOTO"
    OTHER = "OTHER"


class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    DISPATCHER = "DISPATCHER"
    OPERATOR = "OPERATOR"
