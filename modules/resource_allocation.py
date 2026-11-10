def recommend_resources(disaster, severity, affected_people):

    recommendations = {
        "Flood": [
            "Rescue Boats",
            "Ambulances",
            "Food Supplies",
            "Drinking Water",
            "Rescue Teams"
        ],

        "Fire": [
            "Fire Engines",
            "Medical Kits",
            "Ambulances",
            "Firefighters",
            "Rescue Teams"
        ],

        "Earthquake": [
            "Rescue Teams",
            "Ambulances",
            "Medical Kits",
            "Temporary Shelters",
            "Heavy Equipment"
        ],

        "Cyclone": [
            "Emergency Shelters",
            "Food Supplies",
            "Drinking Water",
            "Medical Kits",
            "Rescue Teams"
        ],

        "Landslide": [
            "Rescue Teams",
            "Ambulances",
            "Excavators",
            "Medical Kits",
            "Heavy Equipment"
        ]
    }

    resources = recommendations.get(disaster, [])

    # Additional resources based on severity
    if severity == "Critical":
        resources.extend([
            "Emergency Response Team",
            "Additional Ambulances",
            "Emergency Shelter"
        ])

    elif severity == "High":
        resources.extend([
            "Additional Medical Kits",
            "Rescue Support Team"
        ])

    # Scale response based on affected people
    if affected_people >= 500:
        priority = "Critical Priority"
    elif affected_people >= 100:
        priority = "High Priority"
    elif affected_people >= 20:
        priority = "Medium Priority"
    else:
        priority = "Low Priority"

    return list(dict.fromkeys(resources)), priority