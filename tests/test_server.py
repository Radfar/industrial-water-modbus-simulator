"""Tests for the Zone 01 Modbus device configuration."""

import unittest

from pymodbus.simulator import SimDevice

from src.modbus_server import build_device
from src.register_map import (
    MODBUS_UNIT_ID,
    CoilAddress,
    DiscreteInputAddress,
    HoldingRegisterAddress,
    InputRegisterAddress,
)


class DeviceConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.device = build_device()

    def test_build_device_returns_pymodbus_sim_device(self) -> None:
        self.assertIsInstance(self.device, SimDevice)

    def test_device_uses_documented_unit_id(self) -> None:
        self.assertEqual(self.device.id, MODBUS_UNIT_ID)

    def test_all_four_address_spaces_start_at_zero(self) -> None:
        blocks = self.device.build_device()
        for block_name in ("c", "d", "h", "i"):
            with self.subTest(address_space=block_name):
                self.assertEqual(blocks[block_name][0], 0)

    def test_address_space_sizes_match_register_map(self) -> None:
        blocks = self.device.build_device()
        self.assertEqual(
            len(blocks["c"][1]) - 1,
            max(CoilAddress) + 1,
        )
        self.assertEqual(
            len(blocks["d"][1]) - 1,
            max(DiscreteInputAddress) + 1,
        )
        self.assertEqual(
            len(blocks["h"][1]) - 1,
            max(HoldingRegisterAddress) + 1,
        )
        self.assertEqual(
            len(blocks["i"][1]) - 1,
            max(InputRegisterAddress) + 1,
        )

    def test_initial_setpoints_and_tank_level(self) -> None:
        blocks = self.device.build_device()
        holding = blocks["h"][1]
        inputs = blocks["i"][1]

        self.assertEqual(holding[0:5], [450, 1000, 50, 200, 900])
        self.assertEqual(inputs[0], 750)

    def test_permissive_is_initially_true_and_outputs_are_stopped(self) -> None:
        blocks = self.device.build_device()
        coils = blocks["c"][1]
        discrete_inputs = blocks["d"][1]

        self.assertEqual(coils[0] & 0xFFFF, 0)
        self.assertTrue(discrete_inputs[0] & 0x0008)


if __name__ == "__main__":
    unittest.main()
