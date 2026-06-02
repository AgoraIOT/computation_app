import asyncio
import importlib
import unittest
from unittest.mock import MagicMock, patch

from tests.fakes import (
    FakeDevice,
    FakeTagValue,
    _FakeBusClient,
    _FakeConfig,
    _FakeLogger,
    install_agoraiot_stub,
    install_all_stubs,
    reset_app_modules,
)

install_all_stubs()
reset_app_modules()

import computation_example as ce  # noqa: E402


def _new_service_with_fresh_stubs(config_kwargs=None):
    """Install a fresh set of fakes, reload the module, and return the
    newly-created service plus the installed fakes."""
    stubs = {
        "config": _FakeConfig(**(config_kwargs or {})),
        "bus_client": _FakeBusClient(),
        "logger": _FakeLogger(),
    }
    install_agoraiot_stub(**stubs)
    reset_app_modules()

    global ce
    ce = importlib.import_module("computation_example")
    svc = ce.ComputationExample()
    return svc, stubs, ce


class InitTests(unittest.TestCase):
    def test_happy_init(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        self.assertEqual(svc.factor, 2.0)
        self.assertEqual(svc.input1, "I1")
        self.assertEqual(svc.input2, "I2")
        self.assertEqual(svc.output1, "O1")
        self.assertEqual(svc.output2, "O2")
        self.assertEqual(svc.message_count, 0)

    def test_non_numeric_factor_raises(self):
        cfg = _FakeConfig()
        cfg["AppConfig"]["Factor"] = "not-a-number"
        install_agoraiot_stub(config=cfg)
        reset_app_modules()

        mod = importlib.import_module("computation_example")
        with self.assertRaises(ValueError):
            mod.ComputationExample()

    def test_missing_key_raises_keyerror(self):
        cfg = _FakeConfig()
        del cfg["AppConfig"]["Input1"]
        install_agoraiot_stub(config=cfg)
        reset_app_modules()

        mod = importlib.import_module("computation_example")
        with self.assertRaises(KeyError):
            mod.ComputationExample()


class RunLoopTests(unittest.TestCase):
    def test_run_polls_all_queues_and_exits_when_disconnected(self):
        svc, stubs, mod = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        bus._connect_responses = [True, True, False]
        bus.messages._data = [MagicMock(header=MagicMock(MessageType="IODataReport", MessageID="d", TimeStamp=1), device=[])]
        bus.messages._request = [MagicMock(header=MagicMock(MessageType="IODataReport", MessageID="r", TimeStamp=1), device=[])]
        bus.messages._application = [MagicMock(header=MagicMock(MessageType="NotIODataReport", MessageID="a", TimeStamp=1), device=[])]

        with patch.object(mod.time, "sleep") as sleep_patch:
            asyncio.run(svc.run())
        bus.connect.assert_called_once_with(30)
        self.assertGreaterEqual(sleep_patch.call_count, 1)

    def test_run_exits_immediately_when_not_connected(self):
        svc, stubs, mod = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        bus._connect_responses = [False]
        with patch.object(mod.time, "sleep"):
            asyncio.run(svc.run())
        bus.connect.assert_called_once_with(30)


class MessageHandlerTests(unittest.TestCase):
    def _msg(self, message_type, devices=None):
        return MagicMock(
            header=MagicMock(MessageType=message_type, MessageID="m1", TimeStamp=0),
            device=devices or [],
        )

    def test_non_iodatareport_returns_early(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        svc.agora_message_handler(self._msg("Heartbeat"))
        self.assertEqual(svc.message_count, 1)
        bus.send_data.assert_not_called()

    def test_iodatareport_with_empty_device_list_skips_send(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        svc.agora_message_handler(self._msg("IODataReport", devices=[]))
        bus.send_data.assert_not_called()

    def test_iodatareport_adds_device_and_sends(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        dev = FakeDevice(id=42, tags={
            "I1": FakeTagValue(10),
            "I2": FakeTagValue(4),
        })
        svc.agora_message_handler(self._msg("IODataReport", devices=[dev]))
        bus.send_data.assert_called_once()
        sent = bus.send_data.call_args.args[0]
        # Our fake IoDataReportMsg.add_device_data stores entries
        self.assertEqual(len(sent.device), 1)
        self.assertEqual(sent.device[0]["id"], 42)

    def test_iodatareport_with_devices_but_missing_tags_skips_send(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        bus = stubs["bus_client"]
        dev = FakeDevice(id=99, tags={})  # missing both inputs
        svc.agora_message_handler(self._msg("IODataReport", devices=[dev]))
        bus.send_data.assert_not_called()


class ProcessDeviceTests(unittest.TestCase):
    def test_missing_input1_logs_error_and_returns(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=1, tags={"I2": FakeTagValue(2)})
        svc.process_device(dev, report)
        report.add_device_data.assert_not_called()
        self.assertTrue(any(lvl == "ERROR" for lvl, _ in stubs["logger"].records))

    def test_missing_input2_logs_error_and_returns(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=1, tags={"I1": FakeTagValue(1)})
        svc.process_device(dev, report)
        report.add_device_data.assert_not_called()

    def test_computes_average_and_difference(self):
        svc, stubs, _ = _new_service_with_fresh_stubs()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=2, tags={"I1": FakeTagValue(10), "I2": FakeTagValue(4)})
        svc.process_device(dev, report)
        # factor=2 -> average = 2*(10+4)/2 = 14, difference = 2*(10-4) = 12
        self.assertEqual(report.add_device_data.call_count, 2)
        call1, call2 = report.add_device_data.call_args_list
        # first call outputs average as O1
        self.assertEqual(call1.args[0], 2)
        self.assertEqual(call1.args[1], "O1")
        self.assertEqual(call1.args[2].value, 14)
        self.assertEqual(call2.args[1], "O2")
        self.assertEqual(call2.args[2].value, 12)

    def test_factor_zero_yields_zero_outputs(self):
        cfg = _FakeConfig()
        cfg["AppConfig"]["Factor"] = "0"
        install_agoraiot_stub(config=cfg)
        reset_app_modules()

        mod = importlib.import_module("computation_example")
        svc = mod.ComputationExample()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=1, tags={"I1": FakeTagValue(10), "I2": FakeTagValue(4)})
        svc.process_device(dev, report)
        for call in report.add_device_data.call_args_list:
            self.assertEqual(call.args[2].value, 0)

    def test_equal_inputs_yield_zero_difference(self):
        svc, _, _ = _new_service_with_fresh_stubs()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=3, tags={"I1": FakeTagValue(5), "I2": FakeTagValue(5)})
        svc.process_device(dev, report)
        # factor=2 -> avg = 2*10/2 = 10, diff = 0
        call1, call2 = report.add_device_data.call_args_list
        self.assertEqual(call1.args[2].value, 10)
        self.assertEqual(call2.args[2].value, 0)

    def test_negative_inputs(self):
        svc, _, _ = _new_service_with_fresh_stubs()
        report = MagicMock()
        report.add_device_data = MagicMock()
        dev = FakeDevice(id=4, tags={"I1": FakeTagValue(-6), "I2": FakeTagValue(-4)})
        svc.process_device(dev, report)
        # factor=2 -> avg = 2*(-10)/2 = -10, diff = 2*(-6 - -4) = -4
        call1, call2 = report.add_device_data.call_args_list
        self.assertEqual(call1.args[2].value, -10)
        self.assertEqual(call2.args[2].value, -4)


if __name__ == "__main__":
    unittest.main()
