# Industrial Water Modbus Simulator

A Python-based Modbus TCP device and water-process simulator for the Industrial Water Management testbed.

This repository will host an independent simulated field device. The planned process model includes a pump, control valve, flow rate, and tank level. The simulator will expose process data and commands through a Modbus TCP server so that external clients such as the Node.js Web SCADA and Ignition can connect independently.

## Current status

**Starter project initialized.** The current application is a startup check; the Modbus TCP server, register map, and water-process model have not been implemented yet.

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

## Run

From the repository root:

```powershell
python -m src.main
```

Expected output:

```text
Industrial Water Modbus Simulator
----------------------------------
Python application started successfully.
Modbus library: PyModbus
```

## Planned development

1. Define and document the Modbus data model (coils, discrete inputs, holding registers, and input registers).
2. Implement the Modbus TCP server.
3. Add the simulated water-process behavior (pump, valve, flow, and tank level).
4. Add a Modbus TCP client test and automated tests.
5. Connect the simulator to the Node.js Web SCADA and Ignition as independent Modbus TCP clients.

## Development notes

- The local virtual environment is stored in `.venv/` and must not be committed.
- Python dependencies are recorded in `requirements.txt`.
- The Modbus server will use a configurable TCP port; a non-privileged development port such as 1502 is the initial preference.
