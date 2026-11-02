"""Integration tests for the Zone 01 control/process runtime."""

import unittest

from src.modbus_server import build_device
from src.process_model import WaterProcessModel
from src.register_map import (
    CoilAddress,
    DiscreteInputAddress,
    HoldingRegisterAddress,
    InputRegisterAddress,
)
from src.runtime import Zone01Runtime


class Zone01RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.device = build_device()
        self.runtime = Zone01Runtime(self.device)

    def test_first_scan_publishes_initial_process_state(self):
        state = self.runtime.scan()
        coils, di, hr, ir = self.device.simdata
        self.assertFalse(state.running)
        self.assertTrue(state.permissive)
        self.assertTrue(di[0].values[DiscreteInputAddress.Z01_MANUAL])
        self.assertFalse(di[0].values[DiscreteInputAddress.Z01_RUN_FEEDBACK])
        self.assertEqual(ir[0].values[InputRegisterAddress.Z01_TANK_LEVEL], 750)
        self.assertEqual(ir[0].values[InputRegisterAddress.Z01_FLOW], 0)

    def test_manual_start_runs_process_and_consumes_momentary_coil(self):
        coils = self.device.simdata[0][0].values
        coils[CoilAddress.Z01_START] = True

        state = self.runtime.scan()

        self.assertTrue(state.running)
        self.assertFalse(coils[CoilAddress.Z01_START])
        self.assertTrue(
            self.device.simdata[1][0].values[
                DiscreteInputAddress.Z01_RUN_FEEDBACK
            ]
        )
        self.assertEqual(
            self.device.simdata[3][0].values[InputRegisterAddress.Z01_FLOW],
            900,
        )
        self.assertEqual(
            self.device.simdata[3][0].values[
                InputRegisterAddress.Z01_PUMP_FREQUENCY
            ],
            450,
        )

    def test_manual_stop_stops_process_and_is_consumed(self):
        coils = self.device.simdata[0][0].values
        coils[CoilAddress.Z01_START] = True
        self.runtime.scan()
        coils[CoilAddress.Z01_STOP] = True

        state = self.runtime.scan()

        self.assertFalse(state.running)
        self.assertFalse(coils[CoilAddress.Z01_STOP])
        self.assertFalse(
            self.device.simdata[1][0].values[
                DiscreteInputAddress.Z01_RUN_FEEDBACK
            ]
        )
        self.assertEqual(
            self.device.simdata[3][0].values[InputRegisterAddress.Z01_FLOW],
            0,
        )

    def test_auto_mode_starts_when_tank_is_low(self):
        device = build_device()
        runtime = Zone01Runtime(
            device,
            process_model=WaterProcessModel(initial_tank_level_percent=10.0),
        )
        device.simdata[0][0].values[CoilAddress.Z01_AUTO] = True

        state = runtime.scan()

        self.assertTrue(state.auto_active)
        self.assertTrue(state.running)

    def test_invalid_setpoint_removes_effective_permissive(self):
        coils = self.device.simdata[0][0].values
        holding = self.device.simdata[2][0].values
        coils[CoilAddress.Z01_START] = True
        holding[HoldingRegisterAddress.Z01_PUMP_SPEED_SP] = 600

        state = self.runtime.scan()

        self.assertFalse(state.running)
        self.assertFalse(state.permissive)
        # The external permissive input remains true; setpoint validity is
        # an additional internal condition and does not overwrite that input.
        self.assertTrue(
            self.device.simdata[1][0].values[
                DiscreteInputAddress.Z01_PERMISSIVE
            ]
        )
        self.assertEqual(
            self.device.simdata[3][0].values[InputRegisterAddress.Z01_FLOW],
            0,
        )

    def test_external_permissive_loss_blocks_start(self):
        di = self.device.simdata[1][0].values
        di[DiscreteInputAddress.Z01_PERMISSIVE] = False
        self.device.simdata[0][0].values[CoilAddress.Z01_START] = True

        state = self.runtime.scan()

        self.assertFalse(state.running)
        self.assertFalse(state.permissive)


if __name__ == "__main__":
    unittest.main()
