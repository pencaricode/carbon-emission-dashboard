import sqlite3
import os


# =====================================================
# ENSURE DATABASE FOLDER EXISTS
# =====================================================
os.makedirs(
    "database",
    exist_ok=True
)


# =====================================================
# CONNECT DATABASE
# =====================================================
conn = sqlite3.connect(
    "database/emissions.db",
    check_same_thread=False
)

cursor = conn.cursor()


# =====================================================
# CREATE TABLE
# =====================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS emissions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,

    period TEXT,

    scope1 REAL,

    scope2 REAL,

    scope3 REAL,

    total REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# =====================================================
# INSERT DATA
# =====================================================
def insert_emission(
    company,
    period,
    scope1,
    scope2,
    scope3,
    total
):

    cursor.execute("""
    INSERT INTO emissions (

        company,
        period,
        scope1,
        scope2,
        scope3,
        total

    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        company,
        period,
        scope1,
        scope2,
        scope3,
        total
    ))

    conn.commit()


# =====================================================
# GET ALL DATA
# =====================================================
def get_all_emissions():

    cursor.execute("""
    SELECT *
    FROM emissions
    ORDER BY created_at DESC
    """)

    return cursor.fetchall()


# =====================================================
# GET TREND DATA
# =====================================================
def get_trend_data():

    cursor.execute("""
    SELECT
        created_at,
        total
    FROM emissions
    ORDER BY created_at ASC
    """)

    return cursor.fetchall()


# =====================================================
# DELETE SINGLE DATA BY ID
# =====================================================
def delete_emission_by_id(emission_id):

    cursor.execute("""
    DELETE FROM emissions
    WHERE id = ?
    """, (
        emission_id,
    ))

    conn.commit()


# =====================================================
# RESET ALL DATA
# =====================================================
def reset_all_emissions():

    cursor.execute("""
    DELETE FROM emissions
    """)

    conn.commit()


# =====================================================
# COUNT DATA
# =====================================================
def count_emissions():

    cursor.execute("""
    SELECT COUNT(*)
    FROM emissions
    """)

    return cursor.fetchone()[0]