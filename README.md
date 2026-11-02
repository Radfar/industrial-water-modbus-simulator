# Industrial Water Modbus Simulator

A Python-based Modbus TCP device and water-process simulator for the Industrial Water Management testbed.

This repository hosts an independent simulated field device. The planned process model includes a pump, control valve, flow rate, and tank level. The simulator exposes its initial register map through a Modbus TCP server so external clients such as the Node.js Web SCADA and Ignition can connect independently.

## Current status

**Milestone 1 complete:** initial Modbus register map and scaling helpers defined.

**Milestone 2 implemented:** Modbus TCP server and initial device memory are configured. Local client integration verification is the next task.

See [Zone 01 Modbus TCP Register Map](docs/modbus-register-map.md).

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

Expected startup message:

```text
Industrial Water Modbus Simulator
----------------------------------
Modbus TCP server listening on 127.0.0.1:1502
Unit ID: 1
Press Ctrl+C to stop the server.
```

The server remains active until you press Ctrl+C.

## Verify Modbus TCP communication

Start the server in one terminal:

```powershell
python -m src.main
```

Keep it running. Open a second VS Code terminal, activate the same virtual environment, and run:

```powershell
python -m src.client_check
```

The client check reads all four Modbus data areas, toggles the Auto coil and restores it, then changes the pump-speed setpoint by one register count (0.1 Hz) and restores the original value. It prints PASS only after successful read-back and restoration. Do not stop the server while this check is running.

Discrete inputs and input registers are configured as read-only data areas. Coils and holding registers are writable. This milestone verifies protocol communication and storage only; it does not execute pump/valve process logic.

## Run automated tests

In a second terminal, activate the same virtual environment and run:

```powershell
python -m unittest discover -s tests -v
```

The tests cover register-map helpers and initial device configuration. They do not yet prove end-to-end client communication; that will be verified in the next integration step.

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
| Other measurements/status | 0 / False |

These are startup memory values only. Dynamic process simulation and command handling are not implemented yet. In particular, the server currently stores command-coil writes; it does not yet execute or automatically clear momentary requests.

## Project structure

```text
industrial-water-modbus-simulator/
├── docs/
│   └── modbus-register-map.md
├── src/
│   ├── __init__.py
│   ├── client_check.py
│   ├── main.py
│   ├── modbus_server.py
│   └── register_map.py
├── tests/
│   ├── __init__.py
│   ├── test_register_map.py
│   └── test_server.py
├── requirements.txt
└── README.md
```

## Planned development

1. **Register map:** completed.
2. **Modbus TCP server:** implemented; local client verification pending.
3. Add the simulated water-process behavior (pump, valve, flow, and tank level).
4. Add command processing, momentary request handling, setpoint validation, and process-behavior tests.
5. Connect the simulator to the Node.js Web SCADA and Ignition as independent Modbus TCP clients.

## Development notes

- The local virtual environment is stored in `.venv/` and must not be committed.
- Python dependencies are recorded in `requirements.txt`.
- Default endpoint: `127.0.0.1:1502`, Unit ID 1.
- The register map uses zero-based Modbus PDU offsets; conventional reference numbers are documented alongside them.
- All analog process values are simulated, not physical measurements.
- The server binds to loopback only by default. Do not expose it to an untrusted network.
