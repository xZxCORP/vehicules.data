from dataclasses import dataclass
from typing import Optional


@dataclass
class Risk:
    generic: list[str]
    exterior: list[str]
    generic: list[str]


@dataclass
class Model:
    constructor: str
    model: str
    year: int
    risks: list[Risk]


@dataclass
class Vehicle(Model):
    constructor: str
    model: str
    year: int
    risks: list[Risk]
    sinisters: list
    vin: str
    issues: list[Risk]
