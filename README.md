# FUEL CELL SYSTEM GENERATION

Command:
```
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
python3 main.py
```

Expected output:

```

[
    {
        "classification": "PFD",
        "final_status": "invalid_but_best_effort",
        "iterations": 3,
        "final_graph": [
            {"start_component": "Sea water", "end_component": "Heat Exchanger"},
            {"start_component": "Heat Exchanger", "end_component": "3-way valve"},
            {"start_component": "3-way valve", "end_component": "Coolant Pump"},
            {"start_component": "Coolant Pump", "end_component": "Ion Exchanger"},
            {"start_component": "Ion Exchanger", "end_component": "Fuel Cell Stack"},
            {"start_component": "Fuel Cell Stack", "end_component": "DC/DC Converter"},
            {"start_component": "DC/DC Converter", "end_component": "Electricity"},
            {"start_component": "Hydrogen", "end_component": "Injector"},
            {"start_component": "Injector", "end_component": "Fuel Cell Stack"},
            {"start_component": "Fuel Cell Stack", "end_component": "Gas/water separator"},
            {"start_component": "Gas/water separator", "end_component": "Check Valve"},
            {"start_component": "Check Valve", "end_component": "Pressure Control Valve"},
            {"start_component": "Pressure Control Valve", "end_component": "Exhaust"},
            {"start_component": "Air", "end_component": "Filter"},
            {"start_component": "Filter", "end_component": "Flow meter"},
            {"start_component": "Flow meter", "end_component": "Comp"},
            {"start_component": "Comp", "end_component": "Inter-cooler"},
        ],
        "remaining_violations": [
            {
                "type": "missing_component",
                "description": "Missing cooling loop components.",
                "related_components": ["Coolant Pump", "Flow meter"],
            },
            {
                "type": "invalid_connection",
                "description": "Direct connection of air to Fuel Cell without filtering/compression.",
                "related_components": ["Air", "Fuel Cell Stack"],
            },
            {
                "type": "forbidden_pattern",
                "description": "Fuel and air mixing before Fuel Cell.",
                "related_components": ["Injector", "Filter", "Fuel Cell Stack"],
            },
            {
                "type": "structural_error",
                "description": "Broken cooling loop; not closed.",
                "related_components": ["Coolant Pump", "Flow meter"],
            },
        ],
    }
]

```

Note: 
Paper to read:
- Graph neural network
- Graph convolution network
- Graph attention network + Attention is all you need