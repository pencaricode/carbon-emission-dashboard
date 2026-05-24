from data.emission_factors import *

def kg_to_ton(value):
    return value / 1000


def calculate_scope1_static(fuel, quantity):

    factor = FUEL_DATABASE[fuel]["factor"]

    emission = quantity * factor

    return emission


def calculate_scope1_mobile(
    fuel,
    distance,
    efficiency
):

    fuel_used = distance / efficiency

    factor = FUEL_DATABASE[fuel]["factor"]

    emission = fuel_used * factor

    return emission


def calculate_scope2(kwh):

    return kwh * ELECTRICITY_FACTOR


def calculate_scope3(category, quantity):

    factor = SCOPE3_DATABASE[category]["factor"]

    emission = quantity * factor

    return emission