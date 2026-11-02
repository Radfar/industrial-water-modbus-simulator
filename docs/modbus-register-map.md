# Zone 01 — Modbus TCP Register Map

**Document ID:** IWM-Z01-MODBUS-001  
**Version:** 0.2  
**Status:** Server implemented — integration verification pending

## 1. Purpose

This document defines the Modbus TCP data interface for the Industrial Water Management testbed. The Python application simulates a water process and exposes commands, status, setpoints, and measurements to independent Modbus TCP clients, including the Node.js Web SCADA and Ignition.

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

The server binds to loopback by default. Port 1502 avoids requiring elevated privileges for conventional TCP port 502. Do not expose this development simulator to an untrusted network.

## 3. Addressing convention

The tables show both the zero-based Modbus PDU offset and conventional reference notation.

**Use the zero-based PDU offset in software APIs unless a client explicitly asks for a 0xxxx/1xxxx/3xxxx/4xxxx reference number.** Client configuration terminology differs: some drivers display a reference number, while others ask for a zero-based offset.

The four Modbus data areas are independent. For example, coil offset 0 and holding-register offset 0 are different addresses in different data areas.

## 4. Coils — commands and mode (0xxxx)

Coils are read/write Boolean values.

| PDU offset | Reference | Signal | Access | Meaning |
|---:|---:|---|---|---|
| 0 | 00001 | `Z01_AUTO` | R/W | Mode selection: 1 = Auto, 0 = Manual |
| 1 | 00002 | `Z01_START` | R/W | Start request |
| 2 | 00003 | `Z01_STOP` | R/W | Stop request |
| 3 | 00004 | `Z01_FAULT_RESET` | R/W | Fault-reset request |

### Current server behavior

- `AUTO` is a maintained selection; it is not proof that automatic control is active.
- The server currently provides protocol-level coil storage only. It does not yet execute process commands or automatically consume/clear the three request coils.
- A successful Modbus write confirms protocol-level write handling only. It does not prove that the process accepted or completed the requested action.
- The process-control milestone will implement command handling, pulse consumption, and controller-state feedback.

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

At server startup, all discrete inputs are false except `Z01_PERMISSIVE`, which is initialized true. These are initial memory values, not live process calculations. `RUN_FEEDBACK` is not independent physical feedback.

`COMM_OK` is intentionally not included as a device process bit. Communication availability and data freshness should be determined by each client from connection and polling behavior. `PROCESS_OK` is not a substitute for communication health.

## 6. Holding registers — setpoints (4xxxx)

Holding registers are read/write unsigned 16-bit values. Analog setpoints use a scale factor of 10.

| PDU offset | Reference | Signal | Unit | Scale | Engineering range |
|---:|---:|---|---|---:|---:|
| 0 | 40001 | `Z01_PUMP_SPEED_SP` | Hz | ×10 | 0.0–50.0 |
| 1 | 40002 | `Z01_VALVE_POSITION_SP` | % | ×10 | 0.0–100.0 |
| 2 | 40003 | `Z01_FLOW_LOW_SP` | L/min | ×10 | 0.0–1000.0 |
| 3 | 40004 | `Z01_TANK_LEVEL_LOW_SP` | % | ×10 | 0.0–100.0 |
| 4 | 40005 | `Z01_TANK_LEVEL_HIGH_SP` | % | ×10 | 0.0–100.0 |

Initial values are 45.0 Hz, 100.0%, 5.0 L/min, 20.0%, and 90.0%, respectively. These values are startup defaults, not validated operating recommendations.

The current server stores client writes but does not yet enforce engineering limits or the relationship between low and high tank thresholds. Process validation will be added with the control logic. A Modbus register write alone does not bypass the need for process validation.

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

At startup, tank level is initialized to 75.0%; the other measurement registers are initialized to zero. The values are simulated memory defaults, not physical sensor readings. The process model will update them in a later milestone.

## 8. Data representation and scaling

Each analog value occupies one 16-bit unsigned register. For the default scale factor of 10:

- Engineering value 56.7 is encoded as integer 567.
- Integer 567 is decoded as engineering value 56.7.
- Negative values are not supported by this initial map.
- Process logic must reject values outside the defined engineering range, even if they fit in an unsigned 16-bit register.

The protocol register contains only the scaled number. Signal name, engineering unit, description, and quality must be maintained in the client-side tag mapping/documentation.

## 9. Canonical model and Zone 01 extensions

The map preserves command/status/feedback separation:

- Commands: `AUTO`, `START`, `STOP`, `FAULT_RESET`.
- Status and diagnostics: `RUN_FEEDBACK`, `RUNNING`, `FAULT`, `PERMISSIVE`, `MANUAL`, `AUTO_ACTIVE`, `FLOW_OK`, `LOW_FLOW`, and `PROCESS_OK`.
- Process values: `FLOW` and `VALVE`.
- Zone 01 extensions: tank level, pump speed/frequency/current, pump fault, tank alarms, and equipment setpoints.

Moisture setpoints are not included because this Zone 01 process models tank level rather than a soil-moisture loop.

## 10. Verification status

Implemented:
1. All four address spaces are defined with zero-based offsets.
2. A PyModbus TCP server is configured for loopback, TCP port 1502, Unit ID 1.
3. Initial register and bit values are loaded from the register map.
4. Unit tests validate device identity, address-space sizes, and startup values.

Pending local integration verification:
1. A Modbus TCP client can connect and read each address space.
2. A client can write the Auto coil and holding-register setpoints.
3. Discrete inputs and input registers reject client writes.
4. Node.js and Ignition interpret the same offsets, units, and signal semantics.

Not implemented yet:
- Process simulation and dynamic measurement updates.
- Start/stop/auto/fault-reset control behavior.
- Momentary command consumption and clearing.
- Setpoint engineering validation.
- Client integration and process-behavior tests.

## 11. Change control

This is register-map version 0.2. Changes to offsets, signal meanings, access, units, or scaling require a versioned update and corresponding client mapping changes.
