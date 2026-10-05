def diagnose_vehicle(symptoms):
    symptoms = symptoms.lower()

    diagnosis = "Unable to determine the exact issue."
    severity = "Low"
    confidence = 60
    estimated_cost = "₹500 - ₹2,000"

    recommendations = [
        "Inspect the vehicle carefully.",
        "If the problem continues, consult a qualified mechanic."
    ]

    # Battery / Starting problem
    if any(word in symptoms for word in [
        "battery",
        "not starting",
        "won't start",
        "wont start",
        "starting problem",
        "engine not starting"
    ]):
        diagnosis = "Possible weak or discharged battery."
        severity = "High"
        confidence = 92
        estimated_cost = "₹2,000 - ₹8,000"

        recommendations = [
            "Check the battery voltage.",
            "Inspect battery terminals for corrosion.",
            "Check the alternator charging system.",
            "Replace the battery if it is weak or damaged."
        ]

    # Overheating
    elif any(word in symptoms for word in [
        "overheating",
        "overheat",
        "hot engine",
        "temperature high",
        "engine temperature"
    ]):
        diagnosis = "Possible engine cooling system problem."
        severity = "Critical"
        confidence = 94
        estimated_cost = "₹1,500 - ₹15,000"

        recommendations = [
            "Check coolant level.",
            "Inspect the radiator and cooling fan.",
            "Check for coolant leakage.",
            "Do not continue driving if the engine temperature is extremely high."
        ]

    # Brake problem
    elif any(word in symptoms for word in [
        "brake",
        "brakes",
        "braking",
        "brake noise",
        "brake failure"
    ]):
        diagnosis = "Possible brake system issue."
        severity = "Critical"
        confidence = 95
        estimated_cost = "₹2,000 - ₹12,000"

        recommendations = [
            "Inspect brake pads.",
            "Check brake fluid level.",
            "Inspect brake discs or drums.",
            "Avoid high-speed driving until the brakes are inspected."
        ]

    # Check engine
    elif any(word in symptoms for word in [
        "check engine",
        "engine light",
        "warning light",
        "engine warning"
    ]):
        diagnosis = "Possible engine or sensor-related fault."
        severity = "Medium"
        confidence = 88
        estimated_cost = "₹1,000 - ₹20,000"

        recommendations = [
            "Scan the vehicle using an OBD-II scanner.",
            "Check engine sensors and wiring.",
            "Inspect ignition and fuel systems.",
            "Get a professional diagnostic scan if the warning persists."
        ]

    # Vibration
    elif any(word in symptoms for word in [
        "vibration",
        "shaking",
        "shaking while driving",
        "steering vibration"
    ]):
        diagnosis = "Possible wheel balancing, alignment, tyre, or suspension issue."
        severity = "Medium"
        confidence = 86
        estimated_cost = "₹800 - ₹10,000"

        recommendations = [
            "Check tyre pressure.",
            "Inspect tyres for uneven wear.",
            "Perform wheel balancing.",
            "Check wheel alignment and suspension components."
        ]

    # AC problem
    elif any(word in symptoms for word in [
        "ac",
        "air conditioner",
        "air conditioning",
        "cooling problem",
        "ac not cooling"
    ]):
        diagnosis = "Possible air-conditioning system issue."
        severity = "Medium"
        confidence = 84
        estimated_cost = "₹500 - ₹8,000"

        recommendations = [
            "Check AC refrigerant level.",
            "Inspect the cabin air filter.",
            "Check the AC compressor.",
            "Inspect for refrigerant leakage."
        ]

    # Smoke
    elif any(word in symptoms for word in [
        "smoke",
        "smoking",
        "white smoke",
        "black smoke",
        "blue smoke"
    ]):
        diagnosis = "Possible engine, oil, coolant, or fuel-system problem."
        severity = "High"
        confidence = 90
        estimated_cost = "₹2,000 - ₹30,000"

        recommendations = [
            "Stop the vehicle if heavy smoke is present.",
            "Check engine oil level.",
            "Check coolant level.",
            "Have the engine inspected by a professional mechanic."
        ]

    # Poor mileage
    elif any(word in symptoms for word in [
        "low mileage",
        "poor mileage",
        "fuel consumption",
        "high fuel consumption",
        "less mileage"
    ]):
        diagnosis = "Possible fuel efficiency or engine performance issue."
        severity = "Medium"
        confidence = 82
        estimated_cost = "₹500 - ₹8,000"

        recommendations = [
            "Check tyre pressure.",
            "Replace the air filter if required.",
            "Check spark plugs.",
            "Inspect fuel injectors and sensors."
        ]

    return {
        "diagnosis": diagnosis,
        "severity": severity,
        "confidence": confidence,
        "estimated_cost": estimated_cost,
        "recommendations": recommendations
    }