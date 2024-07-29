import json
import string
import os
import pandas as pd
import numpy as np

from typing import Union
from vehicule_classes import Model, Vehicle


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

VEHICLES_DIR = r"vehicles"


def get_vin():
    # Définir les caractères valides pour un VIN
    characters = [c for c in string.ascii_uppercase + string.digits if c not in "IOQ"]

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
    if size > len(array):
        size = len(array) - 1

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


def set_p_for_brands(df: pd.DataFrame, name: str) -> list[Model]:
    keys = [key for key in ISSUES["generic"]]
    keys.extend([key for key in ISSUES["exterior"]])
    keys.extend([key for key in ISSUES["mechanical"]])

    n = np.random.randint(2, 15)
    constructor_risks: list = generate_choices(keys, size=n, replace=True)

    vehicles = []

    for index, row in df.iterrows():

        n = np.random.randint(2, 5)
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
    model: Model = Model(**model)
    crash_df = pd.read_csv("data/crash.csv")
    rounds = (2024 - model.year) % 5

    car: Union[Vehicle, None] = None

    if rounds <= 0:
        rounds = 1

    sinisters = []
    issues = {"exterior": [], "mechanical": [], "generic": []}

    for _ in range(rounds):
        has_sinister = np.random.choice([True, False], p=[0.25, 0.75])
        if has_sinister:
            accident = crash_df.sample().to_dict()
            sinisters.append(accident)

            key = np.random.choice(["exterior", "mechanical", "generic"])
            issues[key].append(np.random.choice(ISSUES[key]))

    if np.random.choice([True, False], p=[0.45, 0.55]):
        issues[key].append(np.random.choice(model.risks[key]))

    car = Vehicle(
        constructor=model.constructor,
        model=model.model,
        year=model.year,
        risks=model.risks,
        sinisters=sinisters,
        vin=get_vin(),
        issues=issues,
    )

    return car


for filename in os.listdir(VEHICLES_DIR):
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(f"{VEHICLES_DIR}/{filename}")
        df = df.drop_duplicates(subset=["model", "year"])

    # We get every model of the csv
    models = list(set(df["model"].tolist()))
    unique_vehicles = [{"name": x.strip()} for x in models]

    brand_models = set_p_for_brands(df, filename.strip(".csv"))

    for i in range(1, 1000):
        model: Model = np.random.choice(brand_models)
