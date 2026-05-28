import pandas as pd
import sqlite3

# READ CSV FILE
df = pd.read_csv(
    "CSV/BSCPE-1-6.csv"
)

# REMOVE EXTRA SPACES IN COLUMN NAMES
df.columns = df.columns.str.strip()

# DROP ROWS WITH NO STUDENT NUMBER
df = df.dropna(subset=["Student Number"])

# SELECT ONLY NEEDED COLUMNS
df = df[
    [
        "Student Number",
        "Last Name",
        "First Name",
        "Middle Name",
        "Subject Code",
        "Section Code"
    ]
]

# TRIM WHITESPACE FROM ALL CELLS
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# CONNECT DATABASE
conn = sqlite3.connect(
    "database/attendance.db"
)

# SAVE TO DATABASE
df.to_sql(
    "students",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print(
    "Students imported successfully."
)