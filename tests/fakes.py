"""Fake agoraiot module to enable unit testing the edge computation app
without the private SDK.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock


COMPUTATION_APP_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = COMPUTATION_APP_ROOT / "src"


def _ensure_on_path() -> None:
    p = str(SRC_DIR)
    if p not in sys.path:
        sys.path.insert(0, p)


class _FakeLogger:
    def __init__(self):
        self.records: List[Any] = []

    def info(self, msg):
        self.records.append(("INFO", msg))

    def debug(self, msg):
        self.records.append(("DEBUG", msg))

    def error(self, msg):
        self.records.append(("ERROR", msg))


class _FakeMessages:
    def __init__(self):
        self._data: List[Any] = []
        self._request: List[Any] = []
        self._application: List[Any] = []

    def get_data_messages(self):
        return self._data

    def get_request_messages(self):
        return self._request

    def get_application_messages(self):
        return self._application


class _FakeBusClient:
    def __init__(self):
        self.messages = _FakeMessages()
        self._connected = False
        self._connect_responses = [True, False]  # default: connect, then drop
        self.connect = MagicMock(side_effect=self._on_connect)
        self.send_data = MagicMock()

    def _on_connect(self, timeout=None):
        self._connected = True

    def is_connected(self) -> bool:
        if self._connect_responses:
            return self._connect_responses.pop(0)
        return False


class _FakeIoPoint:
    def __init__(self, value=None, quality_code=0, timestamp=None):
        self.value = value
        self.quality_code = quality_code
        self.timestamp = timestamp


class _FakeMessageHeader:
    def __init__(self, MessageType="IODataReport", MessageID="m", TimeStamp=0):
        self.MessageType = MessageType
        self.MessageID = MessageID
        self.TimeStamp = TimeStamp


class _FakeIoDataReportMsg:
    def __init__(self):
        self.header = _FakeMessageHeader()
        self.device: List[Any] = []

    def add_device_data(self, device_id, tag, io_point):
        # tiny implementation to be observable
        for entry in self.device:
            if entry.get("id") == device_id:
                entry["tags"][tag] = io_point
                return
        self.device.append({"id": device_id, "tags": {tag: io_point}})


class _FakeAgoraTimeStamp:
    def __init__(self, value: int = 1):
        self.value = value

    def __int__(self):
        return self.value


class _FakeConfig(dict):
    def __init__(self, **kwargs):
        base: Dict[str, Any] = {
            "Name": "compute-app",
            "AppConfig": {
                "Factor": "2",
                "Input1": "I1",
                "Input2": "I2",
                "Output1": "O1",
                "Output2": "O2",
            },
        }
        base.update(kwargs)
        super().__init__(base)


def install_agoraiot_stub(config: _FakeConfig | None = None,
                          bus_client: _FakeBusClient | None = None,
                          logger: _FakeLogger | None = None) -> types.ModuleType:
    mod = types.ModuleType("agoraiot")
    mod.config = config or _FakeConfig()
    mod.bus_client = bus_client or _FakeBusClient()
    mod.logger = logger or _FakeLogger()
    mod.IoDataReportMsg = _FakeIoDataReportMsg
    mod.IoPoint = _FakeIoPoint
    mod.AgoraTimeStamp = _FakeAgoraTimeStamp
    sys.modules["agoraiot"] = mod
    return mod


def install_all_stubs() -> Dict[str, Any]:
    _ensure_on_path()
    mod = install_agoraiot_stub()
    return {
        "agoraiot": mod,
        "config": mod.config,
        "bus_client": mod.bus_client,
        "logger": mod.logger,
    }


def reset_app_modules() -> None:
    """Drop any cached computation_app source modules so a fresh import picks
    up new fakes."""
    for name in ("computation_example", "main"):
        sys.modules.pop(name, None)


class FakeDevice:
    """Tiny device wrapper with a ``tags`` dict and an ``id``."""

    def __init__(self, id: int, tags: Dict[str, Any] | None = None):
        self.id = id
        self.tags = tags or {}


class FakeTagValue:
    def __init__(self, value):
        self.value = value
