# Industrial Water Modbus Simulator

A Python-based Modbus TCP device and water-process simulator for the Industrial Water Management testbed.

Zone 01 models a pump transferring water through a control valve into a storage tank. The simulated field device exposes commands, setpoints, status, and process measurements to independent clients such as the Node.js Web SCADA and Ignition.

## Current status

- **Milestone 1 — Register map:** complete.
- **Milestone 2 — Modbus TCP server:** implemented and locally verified.
- **Milestone 3 — Process and control integration:** implemented in the repository; the latest integrated test suite still needs to be run locally.

The 500 ms nominal runtime scan connects the command processor, water-process model, and Modbus memory. START, STOP, FAULT_RESET, and RE-ENABLE are momentary requests consumed by the runtime. AUTO is a maintained mode selection. STOP sets a controller-owned operator-stop latch; RE-ENABLE clears it but does not issue START.

## Documentation

- [Zone 01 Modbus TCP Register Map](docs/modbus-register-map.md)
- [Zone 01 Water Process Model](docs/zone01-process-model.md)
- [Zone 01 Control Logic](docs/zone01-control-logic.md)

## Run the browser-based Web GUI

The Node.js Web GUI provides a browser-based process overview, live telemetry, controller/interlock status, operator commands and setpoint controls. It connects to the same Modbus TCP simulator as the desktop GUI and other independent clients.

Architecture:

```text
Browser HMI
    | HTTP REST + WebSocket
    v
Node.js / Express
    | Modbus TCP
    v
Python Zone 01 simulator
127.0.0.1:1502, Unit ID 1
```

The Python simulator remains the single source of truth for process behavior and control logic. The browser application is a Modbus client; it does not duplicate the process model.

Start the Python simulator in one terminal:

```powershell
python -m src.main
```

In a second terminal, start the web application:

```powershell
cd web
npm install
npm start
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000).

Live telemetry is delivered over WebSocket. REST endpoints provide health, process snapshots and whitelisted command/setpoint writes. The desktop GUI, browser GUI and Web SCADA can operate as independent Modbus clients, provided they target the same running simulator.

### Web GUI configuration

| Environment variable | Default | Purpose |
|---|---:|---|
| `WEB_HOST` | `127.0.0.1` | Web server bind address |
| `WEB_PORT` | `3000` | Browser HMI HTTP port |
| `MODBUS_HOST` | `127.0.0.1` | Simulator host |
| `MODBUS_PORT` | `1502` | Modbus TCP port |
| `MODBUS_UNIT_ID` | `1` | Modbus unit identifier |
| `POLL_MS` | `500` | Telemetry polling interval |

If another application already uses port 3000, set a different `WEB_PORT`, for example `$env:WEB_PORT = "3001"` in PowerShell before running `npm start`.

The browser GUI is an engineering/test interface, not a safety-rated operator station. Keep it on a trusted development network and do not expose it to untrusted networks.

## Requirements

- Python 3.15.2 (initial development environment)
- PyModbus 3.16.1
- PySide6 6.8 or newer (below version 7) for the desktop GUI

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

## Run the desktop GUI

The PySide6 desktop application provides a live process overview, Modbus communication status, controller status, operator commands, and process setpoint controls. It starts and stops the simulator process itself and connects to that process as a Modbus TCP client.

From the repository root, with the virtual environment active:

```powershell
python -m gui.main
```

Use **Start Simulator** in the window to launch the Modbus server. The GUI connects to `127.0.0.1:1502`, Unit ID `1`, and polls the four Modbus data areas every 500 ms. Use **Stop Simulator** to stop the managed server process. Closing the GUI also requests simulator shutdown.

**Do not run `python -m src.main` separately when using the GUI-managed mode.** That would start a second server and cause a port conflict. The command-line mode remains available when you want to run the simulator without the desktop application.

The GUI is an independent Modbus TCP client; it does not duplicate or bypass the simulator's process model. Other clients, including the Node.js Web SCADA, can connect to the same running simulator. Treat the GUI as an engineering/test interface, not a safety-rated operator station.

## Run the simulator from the command line

From the repository root, with the virtual environment active:

```powershell
python -m src.main
```

The Modbus TCP server listens on `127.0.0.1:1502`, Unit ID `1`. The Zone 01 runtime starts with it and executes a nominal 500 ms scan. Press Ctrl+C to stop.

## Verify Modbus TCP communication

Start the simulator in one terminal. In a second VS Code terminal, activate the same virtual environment and run:

```powershell
python -m src.client_check
```

The client check reads all four Modbus data areas, toggles the AUTO coil and restores it, then changes the pump-speed setpoint by one register count (0.1 Hz) and restores the original value.

**Important:** the client check is a communication/write test, not a process-control test. It toggles AUTO and changes a setpoint; it does not issue START.

## Run automated tests

With the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

The suite covers:
- Register-map definitions and scaling.
- Modbus device configuration and access permissions.
- Water-process model calculations.
- Manual/automatic command processing, interlocks, and fault handling.
- Runtime integration, command consumption, status publication, and setpoint validation.

These unit tests do not require a running Modbus server.

## Initial values

| Signal | Initial value |
|---|---:|
| External permissive | True |
| Tank level | 75.0% |
| Pump speed setpoint | 45.0 Hz |
| Valve position setpoint | 100.0% |
| Low-flow setpoint | 5.0 L/min |
| Tank low threshold | 20.0% |
| Tank high threshold | 90.0% |

These are simulation startup defaults, not validated operating recommendations.

## Project structure

```text
industrial-water-modbus-simulator/
├── docs/
│   ├── modbus-register-map.md
│   ├── zone01-control-logic.md
│   └── zone01-process-model.md
├── gui/
│   ├── __init__.py
│   ├── main.py
│   ├── modbus_worker.py
│   ├── widgets.py
│   └── window.py
├── web/
│   ├── public/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── styles.css
│   ├── modbus-client.js
│   ├── server.js
│   ├── package.json
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── client_check.py
│   ├── command_processor.py
│   ├── main.py
│   ├── modbus_server.py
│   ├── process_model.py
│   ├── register_map.py
│   └── runtime.py
├── tests/
│   ├── __init__.py
│   ├── test_command_processor.py
│   ├── test_process_model.py
│   ├── test_register_map.py
│   ├── test_runtime.py
│   └── test_server.py
├── requirements.txt
└── README.md
```

## Development roadmap

1. Register map and Modbus TCP server — implemented.
2. Standalone water-process model — implemented.
3. Standalone command processor — implemented.
4. Runtime integration and dynamic Modbus updates — implemented; local verification pending.
5. Verify live Modbus behavior with a client.
6. Connect the simulator to the Node.js Web SCADA and Ignition as independent Modbus TCP clients.
7. Add and locally validate the PySide6 desktop GUI for simulator operation and Modbus monitoring — implemented and locally exercised.
8. Add the Node.js browser Web GUI with REST commands and WebSocket telemetry — implemented; latest compact desktop layout awaits visual confirmation.
9. Expand the process model with additional equipment behavior and diagnostics as the testbed evolves.

## Engineering notes

- The process model is independent of PyModbus and the command processor.
- The current pump model is linear and does not include a hydraulic pump curve, VFD acceleration/deceleration ramp, or tank outflow.
- RUNNING is a controller decision. RUN_FEEDBACK is derived from the simulated pump frequency and is not independent physical feedback.
- The current register map has no external pump-fault input. The pump-fault latch is available for future integration.
- Analog values use unsigned 16-bit registers with a default scale factor of 10.
- Modbus addresses in software are zero-based PDU offsets.
- The server binds to loopback by default. Do not expose this development simulator to an untrusted network.
