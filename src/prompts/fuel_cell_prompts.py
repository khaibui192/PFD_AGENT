SYSTEM_PROMPT = """

## Context
The system may include the following subsystems:
- AIR SYSTEM
- FUEL STORAGE SYSTEM
- FUEL DELIVERY SYSTEM
- FUEL CELL STACK (CORE)
- HUMIDIFICATION SYSTEM
- STACK COOLING SYSTEM
- THERMAL CONTROL SYSTEM
- BUS COOLING SYSTEM
- HVAC SYSTEM
- LUBRICATION SYSTEM
- HYDRAULIC SYSTEM
- ELECTRICAL SYSTEM
- CONTROL SYSTEM
- LEAK DETECTION SYSTEM
- FIRE SUPPRESSION SYSTEM

## Constraints and Rulé

1.Compulsory constraint
- The system must contain:
  + Fuel
  + Oxidant (Air)
  + Coolant
  

## Instructions

1. Identify all components (devices, units, equipment) in the diagram.
2. Identify all directional connections (flows, pipes, wires, signals) between components.
3. Respect the direction of flow:
   - If flow goes from A --> B, then:
     "start_component" = A
     "end_component" = B
4. If a component connects to multiple components, list each connection separately.
5. Ignore labels, annotations, or text that do not represent actual connections.
6. If arrows are not clear, infer direction based on standard engineering logic (e.g., fuel flows from storage --> delivery --> stack).
7. Normalize component names (remove IDs if necessary, but keep them if they help distinguish components).
8. Do NOT invent components or connections not present in the diagram.

## Output Format (STRICT)

Process flow diagram (PFD) simulation:

Device A ---> Device B ---> Device C
                |
                `---> Device D


Return ONLY a valid JSON array in the following format:
```

  [
    {
      "start_component": "Device A",
      "end_component": "Device B"
    },
    {
      "start_component": "Device B",
      "end_component": "Device C"
    },
    {
      "start_component": "Device B",
      "end_component": "Device D"
    }
  ]
- No explanations
- No extra text
- No markdown
- No comments

```

## IMPORTANT RULES

- Do NOT invent components
- Do NOT assume connections not present
- If uncertain, mark as "unknown"
- A component may belong to multiple subsystems
- The fuel cell stack is the central node, not a subsystem

## GOAL

Produce a complete list of all directed connections in the system diagram.

Ensure the system:
- is physically valid
- respects engineering constraints
- has correct flow dependencies
- is safe and operable

"""

FUEL_CELL_CONSTRAINT = """

## HARD CONSTRAINT RULES (must NOT be violated)

1. The fuel cell stack MUST receive:
   - fuel
   - oxidant (air)
   - coolant

2. Fuel and oxidant MUST NOT mix before entering the stack.

3. The stack MUST NOT operate without:
   - cooling system active
   - proper flow control

4. Reactants MUST be:
   - regulated in pressure
   - regulated in flow rate
   - controlled in temperature
   - (optionally) humidified

5. The system MUST include control mechanisms to:
   - monitor temperature, pressure, flow
   - shut down in unsafe conditions

## DEPENDENCY RULES (component relationships)

You MUST infer directional dependencies between components.

### 1.Fuel path
Fuel Tank --> Pump --> Flow Controller --> (Heater/Humidifier) --> Fuel Cell

Rules:
- Fuel MUST pass through delivery system before reaching stack
- Direct tank --> stack connection is INVALID

### 2.Air path
Air --> Filter --> Compressor --> Humidifier --> Fuel Cell

Rules:
- Air MUST be filtered before entering stack
- Compressor is required if pressure is needed

### 3.Cooling loop
Pump --> Fuel Cell --> Radiator --> (back to Pump)

Rules:
- Cooling loop MUST be closed
- Pump MUST run when stack is operating
- Radiator or heat exchanger MUST exist

### 4.Electrical path
Fuel Cell --> Power Conditioning --> Load

Rules:
- Output voltage MUST be regulated before reaching load
- Direct connection to sensitive load is NOT recommended

## FAILURE / FORBIDDEN CONDITIONS

Detect and flag:

- Fuel starvation (insufficient fuel flow)
- Air starvation (insufficient oxidant)
- Overheating (no cooling or poor heat rejection)
- Dry membrane (no humidification when required)
- Flooding (excess water accumulation)
- Mixing fuel and air before reaction zone
- Missing control system
- Missing safety shutdown logic

## DESIGN PRINCIPLES

- Subsystems are interconnected and operate simultaneously
- Components may belong to multiple subsystems
- The system is multi-loop (fuel + air + cooling + control)
- Uniform distribution of reactants is critical for performance
- System design must consider coupled interactions across domains

"""