import json
import string
import os
import pandas as pd
import numpy as np

from vehicule_classes import Model


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


CRASHES_FILE = open("crash/crash.csv")
VEHICLES_DIR = r"vehicles"


def get_vin():
    # Définir les caractères valides pour un VIN
    characters = "".join(
        [c for c in string.ascii_uppercase + string.digits if c not in "IOQ"]
    )

    # Générer chaque section du VIN
    # WMI (3 caractères)
    wmi = "".join(np.random.choice(characters, size=3))
    # VDS (6 caractères)
    vds = "".join(np.random.choice(characters, size=6))
    # VIS (8 caractères)
    vis = "".join(np.random.choice(characters, size=8))
    # Combiner les sections pour former le VIN complet
    vin = wmi + vds + vis

    return vin


def generate_choices(array: list, size, replace=False):
    p = np.random.rand(len(array))
    final_p = p / np.sum(p)

    choices: list = np.random.choice(
        a=array, p=final_p, size=size, replace=replace
    ).tolist()

    return choices


def reassign_risks_categories(risks: list[str]):
    output = {"exterior": [], "mechanical": [], "generic": []}
    key = "generic"

    for risk in risks:
        if risk in ISSUES["exterior"]:
            key = "exterior"
        elif risk in ISSUES["mechanical"]:
            key = "mechanical"

        output[key].append(risk)

    return output


def set_p_for_brands(df: pd.DataFrame, name: str):
    keys = [key for key in ISSUES["generic"]]
    keys.extend([key for key in ISSUES["exterior"]])
    keys.extend([key for key in ISSUES["mechanical"]])

    n = np.random.randint(2, 15)
    constructor_risks: list = generate_choices(keys, size=n, replace=True)

    vehicles = []

    for index, row in df.iterrows():

        n = np.random.randint(2, 5)
        model_risks_choices = []

        model_risks_choices = generate_choices(constructor_risks, size=n)

        vehicles.append(
            {
                "constructor": name.strip(".csv"),
                "model": row["model"].strip(),
                "year": row["year"],
                "risks": reassign_risks_categories(model_risks_choices),
            }
        )

    file = open(f"{name}-p.json", "w+")
    file.write(json.dumps(vehicles))

    return vehicles


def generate_car(model: dict):
    df = pd.read_csv(f"data/crash.csv")

    return


for filename in os.listdir(VEHICLES_DIR):
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(f"{VEHICLES_DIR}/{filename}")
        df = df.drop_duplicates(subset=["model", "year"])

    # We get every model of the csv
    models = list(set(df["model"].tolist()))
    unique_vehicles = [{"name": x.strip()} for x in models]

    set_p_for_brands(df, filename.strip(".csv"))
