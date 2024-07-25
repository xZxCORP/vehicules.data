import json
import os
import random
import pandas as pd
import numpy

ISSUES = {
    "exterior": [
        "FRONT_BUMPER",
        "REAR_BUMPER",
        "LEFT_FENDER",
        "RIGHT_FENDER",
        "HOOD",
        "TRUNK",
        "LEFT_DOOR_FRONT",
        "RIGHT_DOOR_FRONT",
        "LEFT_DOOR_REAR",
        "RIGHT_DOOR_REAR",
        "WINDSHIELD",
        "REAR_WINDSHIELD",
    ],
    "mechanical": [
        "ENGINE_FAILURE",
        "TRANSMISSION_DAMAGE",
        "BRAKE_SYSTEM",
        "SUSPENSION_FAILURE",
        "BATTERY_ISSUE",
        "EXHAUST_LEAK",
        "FUEL_SYSTEM",
        "COOLING_SYSTEM",
        "ALTERNATOR_ISSUE",
        "STARTER_PROBLEM",
        "STEERING_FAILURE",
        "CLUTCH_PROBLEM",
    ],
    "generic": [
        "STRUCTURAL_DAMAGE",
        "UNKNOWN_DAMAGE",
        "PAINT_SCRATCHES",
        "DENTED_BODY",
    ],
}


CRASH_KEYS = {
    "Year",
    "Month",
    "Day",
    "Weekend?",
    "Hour",
    "Collision Type",
    "Injury Type",
    "Primary Factor",
    "Reported_Location",
    "Latitude",
    "Longitude",
}

VEHICLE_KEYS = {
    "model",
    "year",
    "price",
    "transmission",
    "mileage",
    "fuelType",
    "tax",
    "mpg",
    "engineSize",
}


csv_directory = r"vehicles"

for filename in os.listdir(csv_directory):
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(f"{csv_directory}/{filename}")

    # We get every model of the csv
    models = list(set(df["model"].tolist()))
    unique_vehicles = [{"name": x.strip()} for x in models]

    keys = [key for key in ISSUES.keys()]
    constructor_risks = random.choices(keys, k=random.randint(1, 3))
    risks_length = len(keys)

    vehicles = []
    for index, row in df.iterrows():

        risks = []
        for i in range(1, len(constructor_risks)):
            risks.append(
                {
                    constructor_risks[i]: numpy.random.choice(
                        ISSUES[constructor_risks[i]],
                        random.randint(len(constructor_risks) - i, 5),
                    ).tolist()
                }
            )

        vehicles.append(
            {
                "constructor": filename.strip(".csv"),
                "model": row["model"].strip(),
                "year": row["year"],
                "risks": risks,
            }
        )

file = open("output.json", "w+")
file.write(json.dumps(vehicles))
