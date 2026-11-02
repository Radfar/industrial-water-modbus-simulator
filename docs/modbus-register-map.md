# Zone 01 — Modbus TCP Register Map

**Document ID:** IWM-Z01-MODBUS-001  
**Version:** 0.1  
**Status:** Initial design baseline — pending integration verification

## 1. Purpose

This document defines the first Modbus TCP data interface for the Industrial Water Management testbed. The Python application will simulate a water process and expose its commands, status, setpoints, and measurements to independent Modbus TCP clients, including the Node.js Web SCADA and Ignition.

The register map is a protocol representation of the Zone 01 logical process model. It does not replace the common process contract.

## 2. Connection parameters

| Parameter | Initial value |
|---|---|
| Protocol | Modbus TCP |
| Development host | 127.0.0.1 |
| TCP port | 1502 |
| Unit ID | 1 |
| Register width | 16 bits |
| Register encoding | Unsigned integer |
| Default analog scaling | Engineering value × 10 |

Port 1502 is selected for local development to avoid requiring elevated privileges for the conventional TCP port 502. The server should initially bind to loopback only; do not expose this simulator to an untrusted network.

## 3. Addressing convention

The tables show both the zero-based Modbus PDU offset and the conventional reference notation.

**Use the zero-based PDU offset in software APIs unless a client explicitly asks for a 0xxxx/1xxxx/3xxxx/4xxxx reference number.** Client configuration terminology differs: some drivers display a reference number, while others ask for a zero-based offset.

The four Modbus data areas are independent. For example, coil offset 0 and holding-register offset 0 are different addresses in different data areas.

## 4. Coils — commands and mode (0xxxx)

Coils are read/write Boolean values. They are used for operator requests and mode selection.

| PDU offset | Reference | Signal | Access | Meaning |
|---:|---:|---|---|---|
| 0 | 00001 | `Z01_AUTO` | R/W | Mode selection: 1 = Auto, 0 = Manual |
| 1 | 00002 | `Z01_START` | R/W pulse | Momentary start request |
| 2 | 00003 | `Z01_STOP` | R/W pulse | Momentary stop request |
| 3 | 00004 | `Z01_FAULT_RESET` | R/W pulse | Momentary fault-reset request |

### Command handling

- `AUTO` is a maintained selection; it is not proof that automatic control is active.
- `START`, `STOP`, and `FAULT_RESET` are momentary requests.
- The simulator should consume and clear momentary command coils after processing them.
- A successful Modbus write confirms protocol-level write handling only. It does not prove that the process accepted or completed the requested action.
- The resulting controller state and feedback must be read separately.

## 5. Discrete inputs — status and feedback (1xxxx)

Discrete inputs are read-only Boolean values.

| PDU offset | Reference | Signal | Meaning |
|---:|---:|---|---|
| 0 | 10001 | `Z01_RUN_FEEDBACK` | Simulated run feedback |
| 1 | 10002 | `Z01_RUNNING` | Controller process-running state |
| 2 | 10003 | `Z01_FAULT` | Aggregated zone fault |
| 3 | 10004 | `Z01_PERMISSIVE` | Conditions permit operation |
| 4 | 10005 | `Z01_MANUAL` | Manual mode status |
| 5 | 10006 | `Z01_AUTO_ACTIVE` | Automatic control is actually active |
| 6 | 10007 | `Z01_FLOW_OK` | Flow satisfies the configured evaluation rule |
| 7 | 10008 | `Z01_LOW_FLOW` | Low-flow diagnostic |
| 8 | 10009 | `Z01_PROCESS_OK` | Aggregate process status |
| 9 | 10010 | `Z01_PUMP_FAULT` | Simulated pump fault |
| 10 | 10011 | `Z01_TANK_LOW` | Tank low-level condition |
| 11 | 10012 | `Z01_TANK_HIGH` | Tank high-level condition |
| 12 | 10013 | `Z01_VALVE_OPEN_FB` | Valve-open status derived from simulated position |

`RUN_FEEDBACK` is simulated in this virtual device; it is not independent physical feedback. `RUNNING` remains the controller state. These signals must not be treated as commands.

`COMM_OK` is intentionally not included as a device process bit. Communication availability and data freshness should be determined by each client from connection and polling behavior. `PROCESS_OK` is not a substitute for communication health.

## 6. Holding registers — setpoints (4xxxx)

Holding registers are read/write unsigned 16-bit values. Analog setpoints use a scale factor of 10 unless otherwise stated.

| PDU offset | Reference | Signal | Unit | Scale | Engineering range |
|---:|---:|---|---|---:|---:|
| 0 | 40001 | `Z01_PUMP_SPEED_SP` | Hz | ×10 | 0.0–50.0 |
| 1 | 40002 | `Z01_VALVE_POSITION_SP` | % | ×10 | 0.0–100.0 |
| 2 | 40003 | `Z01_FLOW_LOW_SP` | L/min | ×10 | 0.0–1000.0 |
| 3 | 40004 | `Z01_TANK_LEVEL_LOW_SP` | % | ×10 | 0.0–100.0 |
| 4 | 40005 | `Z01_TANK_LEVEL_HIGH_SP` | % | ×10 | 0.0–100.0 |

Example: a pump speed setpoint of 35.5 Hz is transmitted as integer 355.

The simulator must validate engineering limits and relationships (for example, low tank-level threshold must be below high threshold) before applying a setpoint. A Modbus register write alone does not bypass process validation.

## 7. Input registers — process measurements (3xxxx)

Input registers are read-only unsigned 16-bit values. Values use a scale factor of 10.

| PDU offset | Reference | Signal | Unit | Scale | Engineering range |
|---:|---:|---|---|---:|---:|
| 0 | 30001 | `Z01_TANK_LEVEL` | % | ×10 | 0.0–100.0 |
| 1 | 30002 | `Z01_FLOW` | L/min | ×10 | 0.0–1000.0 |
| 2 | 30003 | `Z01_PUMP_FREQUENCY` | Hz | ×10 | 0.0–50.0 |
| 3 | 30004 | `Z01_PUMP_SPEED` | % | ×10 | 0.0–100.0 |
| 4 | 30005 | `Z01_VALVE` | % | ×10 | 0.0–100.0 |
| 5 | 30006 | `Z01_PUMP_CURRENT` | A | ×10 | 0.0–100.0 |

These are simulated process measurements, not physical sensor readings. The simulator documentation and HMI should label them as simulated.

## 8. Data representation and scaling

Each analog value occupies one 16-bit unsigned register. For the default scale factor of 10:

- Engineering value 56.7 is encoded as integer 567.
- Integer 567 is decoded as engineering value 56.7.
- Negative values are not supported by this initial map.
- Values outside the defined engineering range must be rejected by process validation, even if they fit in an unsigned 16-bit register.

The protocol register contains only the scaled number. Signal name, engineering unit, description, and quality must be maintained in the client-side tag mapping/documentation.

## 9. Canonical model and Zone 01 extensions

The map preserves the common command/status/feedback separation:

- Common commands: `AUTO`, `START`, `STOP`, `FAULT_RESET`.
- Common status and diagnostics: `RUN_FEEDBACK`, `RUNNING`, `FAULT`, `PERMISSIVE`, `MANUAL`, `AUTO_ACTIVE`, `FLOW_OK`, `LOW_FLOW`, and `PROCESS_OK`.
- Common process values: `FLOW` and `VALVE`.
- Zone 01 process extensions: tank level, pump speed/frequency/current, pump fault, tank alarms, and equipment setpoints.

Moisture setpoints are not included in this initial water-process map because this simulated process currently models tank level rather than soil moisture. Add them only if the Zone 01 process scope requires an irrigation/soil-moisture loop.

## 10. Initial acceptance checks

The following checks are planned; they are not yet executed:

1. All four address spaces use unique, zero-based offsets.
2. A client can read each status and measurement area.
3. A client can write the Auto coil and setpoint holding registers.
4. Momentary command coils are consumed and cleared by the simulator.
5. Out-of-range setpoints are rejected by process logic.
6. Scaled register values decode to the documented engineering units.
7. Node.js and Ignition interpret the same offsets, units, and signal semantics.
8. Communication loss is represented as client-side stale/unavailable quality, not as a false process fault.

## 11. Change control

This is register-map version 0.1. Changes to offsets, signal meanings, access, units, or scaling require a versioned update and corresponding client mapping changes. Reserved offsets may be added later without renumbering existing signals.
