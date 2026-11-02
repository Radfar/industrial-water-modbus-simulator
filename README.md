# Industrial Water Modbus Simulator

A Python-based Modbus TCP device and water-process simulator for the Industrial Water Management testbed.

This repository hosts an independent simulated field device. Zone 01 models a pump transferring water through a control valve into a storage tank. The Modbus TCP interface is intended for independent clients such as the Node.js Web SCADA and Ignition.

## Current status

**Milestone 1 complete:** initial Modbus register map and scaling helpers defined.

**Milestone 2 verified:** Modbus TCP server, device memory, and client read/write checks completed locally.

**Milestone 3 in progress:** standalone water-process model implemented with unit tests. It is not yet connected to the Modbus server or command processor.

See:
- [Zone 01 Modbus TCP Register Map](docs/modbus-register-map.md)
- [Zone 01 Water Process Model](docs/zone01-process-model.md)

## Requirements

- Python 3.15.2 (initial development environment)
- PyModbus 3.16.1

## Setup

Clone the repository and open a terminal in its root directory.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Modbus TCP server

From the repository root, with the virtual environment active:

```powershell
python -m src.main
```

The server listens on 127.0.0.1:1502, Unit ID 1, until Ctrl+C is pressed.

## Verify Modbus TCP communication

Start the server in one terminal. In a second VS Code terminal, activate the same virtual environment and run:

```powershell
python -m src.client_check
```

The client check reads all four Modbus data areas, toggles the Auto coil and restores it, then changes the pump-speed setpoint by one register count (0.1 Hz) and restores the original value.

Discrete inputs and input registers are read-only. Coils and holding registers are writable. The server currently stores command-coil writes; process command handling is not yet integrated.

## Run automated tests

With the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

Tests cover register-map helpers, initial device configuration, and the standalone process model. The process-model tests do not require a running Modbus server.

## Initial device values

| Signal | Initial value |
|---|---:|
| Permissive | True |
| Tank level | 75.0% |
| Pump speed setpoint | 45.0 Hz |
| Valve position setpoint | 100.0% |
| Low-flow setpoint | 5.0 L/min |
| Tank low threshold | 20.0% |
| Tank high threshold | 90.0% |

These are startup memory values. The standalone process model has its own initial state and is not yet synchronized with Modbus device memory.

## Project structure

```text
industrial-water-modbus-simulator/
├── docs/
│   ├── modbus-register-map.md
│   └── zone01-process-model.md
├── src/
│   ├── __init__.py
│   ├── client_check.py
│   ├── main.py
│   ├── modbus_server.py
│   ├── process_model.py
│   └── register_map.py
├── tests/
│   ├── __init__.py
│   ├── test_process_model.py
│   ├── test_register_map.py
│   └── test_server.py
├── requirements.txt
└── README.md
```

## Development roadmap

1. **Register map:** complete.
2. **Modbus TCP server and client verification:** complete locally.
3. **Standalone process model:** implemented; local test execution pending.
4. Add command processing, automatic level control, interlocks, fault handling, and setpoint validation.
5. Integrate the process model with the Modbus server and publish dynamic measurements/status.
6. Connect the simulator to the Node.js Web SCADA and Ignition as independent Modbus TCP clients.

## Development notes

- The local virtual environment is stored in .venv/ and must not be committed.
- Python dependencies are recorded in requirements.txt.
- Default endpoint: 127.0.0.1:1502, Unit ID 1.
- The register map uses zero-based Modbus PDU offsets; conventional reference numbers are documented alongside them.
- All analog process values are simulated, not physical measurements.
- The server binds to loopback only by default. Do not expose it to an untrusted network.
