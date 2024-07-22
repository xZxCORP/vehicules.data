import os
import random
import pandas as pd


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

    vehicles = []
    for index, row in df.iterrows():
        vehicles.append(
            {
                "constructor": filename.strip(".csv"),
                "model": row["model"].strip(),
                "year": row["year"],
            }
        )
