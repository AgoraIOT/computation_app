import importlib
import runpy
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tests.fakes import install_all_stubs, reset_app_modules

install_all_stubs()
reset_app_modules()

SRC = Path(__file__).resolve().parent.parent / "src"


class MainImportTests(unittest.TestCase):
    def test_import_does_not_run_loop(self):
        """Importing ``main`` as a module must not start the asyncio loop."""
        reset_app_modules()
        with patch("asyncio.get_event_loop") as gel:
            importlib.import_module("main")
            gel.assert_not_called()


class MainDunderExecutionTests(unittest.TestCase):
    def test_run_as_main_schedules_task_and_runs_forever(self):
        """Execute main.py as ``__main__`` while patching asyncio and
        ``ComputationExample`` so nothing really blocks."""
        loop = MagicMock()
        loop.create_task = MagicMock()
        loop.run_forever = MagicMock()

        reset_app_modules()
        install_all_stubs()

        with patch("asyncio.get_event_loop", return_value=loop) as gel, \
             patch("asyncio.iscoroutine", return_value=True), \
             patch("builtins.print") as print_patch:
            # patch computation_example.ComputationExample so it's observable
            mod = importlib.import_module("computation_example")

            async def _fake_run():
                return None

            fake_instance = MagicMock()
            fake_instance.run = _fake_run
            with patch.object(mod, "ComputationExample", return_value=fake_instance) as Cls:
                runpy.run_path(str(SRC / "main.py"), run_name="__main__")

            gel.assert_called_once()
            loop.run_forever.assert_called_once()
            loop.create_task.assert_called_once()
            # the name of the module was printed
            self.assertTrue(print_patch.called)
            Cls.assert_called_once()


if __name__ == "__main__":
    unittest.main()
