FUEL_DATABASE = {
    "Batubara": {"unit": "kg", "factor": 1.974},
    "Briket Batubara": {"unit": "kg", "factor": 2.018},
    "Arang": {"unit": "kg", "factor": 3.304},
    "Gas Alam": {"unit": "Nm3", "factor": 2.150},
    "LPG": {"unit": "kg", "factor": 3.015},
    "LGV": {"unit": "kg", "factor": 3.004},
    "LNG": {"unit": "kg", "factor": 2.699},
    "Bensin RON 98": {"unit": "liter", "factor": 2.310},
    "Bensin RON 92": {"unit": "liter", "factor": 2.305},
    "Bensin RON 90": {"unit": "liter", "factor": 2.309},
    "Bensin RON 88": {"unit": "liter", "factor": 2.315},
    "Avtur": {"unit": "liter", "factor": 2.549},
    "Minyak Tanah": {"unit": "liter", "factor": 2.553},
    "Minyak Solar CN 53": {"unit": "liter", "factor": 2.626},
    "Minyak Solar CN 51": {"unit": "liter", "factor": 2.650},
    "Minyak Solar CN 48": {"unit": "liter", "factor": 2.673},
    "Minyak Diesel": {"unit": "liter", "factor": 2.779},
    "Minyak Bakar": {"unit": "liter", "factor": 3.100},
}

SCOPE3_DATABASE = {
    "Transportasi pihak ketiga": {
        "unit": "km",
        "factor": 0.180,
    },
    "Limbah operasional": {
        "unit": "kg",
        "factor": 0.420,
    },
    "Komuter karyawan": {
        "unit": "km",
        "factor": 0.150,
    },
    "Pembelian barang dan jasa": {
        "unit": "juta rupiah",
        "factor": 0.320,
    },
}

ELECTRICITY_FACTOR = 0.790