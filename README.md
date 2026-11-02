# Industrial Water Modbus Simulator

A Python-based Modbus TCP device and water-process simulator for the Industrial Water Management testbed.

This repository hosts an independent simulated field device. The planned process model includes a pump, control valve, flow rate, and tank level. The simulator will expose process data and commands through a Modbus TCP server so that external clients such as the Node.js Web SCADA and Ignition can connect independently.

## Current status

**Milestone 1 complete: initial Modbus register map defined.** The address map, signal semantics, units, scaling, and initial register-address/scaling tests are documented. The Modbus TCP server and dynamic water-process model have not been implemented yet.

See [Zone 01 Modbus TCP Register Map](docs/modbus-register-map.md).

## Requirements

- Python 3.15.2 (initial development environment)
- PyModbus 3.16.1

## Setup

Clone the repository and open a terminal in its root directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the starter application

From the repository root:

```powershell
python -m src.main
```

## Run automated tests

```powershell
python -m unittest discover -s tests -v
```

The current tests verify register-address uniqueness and analog scaling helpers. They do not yet test a running Modbus TCP server.

## Project structure

```text
industrial-water-modbus-simulator/
├── docs/
│   └── modbus-register-map.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── register_map.py
├── tests/
│   ├── __init__.py
│   └── test_register_map.py
├── requirements.txt
└── README.md
```

## Planned development

1. **Register map — initial version defined:** coils, discrete inputs, holding registers, and input registers.
2. Implement the Modbus TCP server using the documented map.
3. Add the simulated water-process behavior (pump, valve, flow, and tank level).
4. Add Modbus TCP client integration tests and process-behavior tests.
5. Connect the simulator to the Node.js Web SCADA and Ignition as independent Modbus TCP clients.

## Development notes

- The local virtual environment is stored in `.venv/` and must not be committed.
- Python dependencies are recorded in `requirements.txt`.
- The initial Modbus TCP development endpoint is `127.0.0.1:1502`, Unit ID 1.
- The register map uses zero-based Modbus PDU offsets; conventional reference numbers are documented alongside them.
- All analog process values in this virtual device are simulated, not physical measurements.
