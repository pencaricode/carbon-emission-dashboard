import random
import sqlite3
from datetime import datetime, timedelta


# =====================================================
# CONNECT DATABASE
# =====================================================
conn = sqlite3.connect(
    "database/emissions.db"
)

cursor = conn.cursor()


# =====================================================
# DUMMY COMPANIES
# =====================================================
companies = [
    "PT Energi Nusantara",
    "PT Green Manufacturing",
    "PT Logistik Indonesia",
    "PT Retail Modern",
    "PT Teknologi Digital",
    "PT Semen Nasional",
    "PT Kimia Industri",
    "PT Food Supply",
]

# =====================================================
# GENERATE DUMMY DATA
# =====================================================
for i in range(120):

    company = random.choice(companies)

    # Random historical date
    random_days = random.randint(0, 365)

    created_at = (
        datetime.now() -
        timedelta(days=random_days)
    )

    period = str(created_at.year)

    # =================================================
    # REALISTIC EMISSION VALUES
    # =================================================
    scope1 = round(
        random.uniform(50, 1500),
        2
    )

    scope2 = round(
        random.uniform(20, 1200),
        2
    )

    scope3 = round(
        random.uniform(5, 500),
        2
    )

    total = round(
        scope1 +
        scope2 +
        scope3,
        2
    )

    # =================================================
    # INSERT DATA
    # =================================================
    cursor.execute("""
    INSERT INTO emissions (

        company,
        period,
        scope1,
        scope2,
        scope3,
        total,
        created_at

    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        period,
        scope1,
        scope2,
        scope3,
        total,
        created_at
    ))

# =====================================================
# SAVE
# =====================================================
conn.commit()

conn.close()

print("Dummy data berhasil ditambahkan.")