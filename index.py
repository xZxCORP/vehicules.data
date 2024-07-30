import json
import string
import os
import pandas as pd
import numpy as np

from tqdm import tqdm
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

VEHICLES_DIR = r"data/brands"


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


def generate_choices(array: list, size=2, replace=False):
    if len(array) < 1:
        return []
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

    file = open(f"data/output/{name}-p.json", "w+")
    file.write(json.dumps(vehicles))

    return vehicles


def crash_to_dict(df: pd.DataFrame) -> dict:
    crash_dict = {}
    vehicle: dict = df.to_dict()
    for key in vehicle.keys():
        crash_dict[key] = list(vehicle[key].values())[0]

    return crash_dict


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
            accident = crash_to_dict(crash_df.sample())

            if accident["Year"] < model.year:
                accident["Year"] = np.random.randint(model.year, 2024)

            sinisters.append(accident)

            key = np.random.choice(["exterior", "mechanical", "generic"])

            issues[key].append(np.random.choice(ISSUES[key]))

    if np.random.choice([True, False], p=[0.45, 0.55]):
        key = np.random.choice(["exterior", "mechanical", "generic"])
        values = model.risks.get(key) if model.risks.get(key) else ISSUES["generic"]
        issues[key].append(np.random.choice(values))

    car = Vehicle(
        constructor=model.constructor,
        model=model.model,
        year=model.year,
        risks=model.risks,
        sinisters=sinisters,
        vin=get_vin(),
        issues=issues,
    )

    return {
        "constructor": car.constructor,
        "model": car.model,
        "year": car.year,
        "risks": car.risks,
        "sinisters": car.sinisters,
        "vin": car.vin,
        "issues": car.issues,
    }


CARS_FILE = open("./data/output/cars.json", "w+")

car_models = []
for filename in os.listdir(VEHICLES_DIR):
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(f"{VEHICLES_DIR}/{filename}")
        df = df.drop_duplicates(subset=["model", "year"])
    print(filename)
    # We get every model of the csv
    models = list(set(df["model"].tolist()))
    unique_vehicles = [{"name": x.strip()} for x in models]

    car_models.extend(set_p_for_brands(df, filename.strip(".csv")))

    cars = []


for i in tqdm(range(100)):
    model: Model = np.random.choice(car_models)
    cars.append(generate_car(model))
CARS_FILE.write(json.dumps(cars))
