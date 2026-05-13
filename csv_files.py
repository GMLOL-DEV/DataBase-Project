import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Pakistankpk@1',
    database='judicial_case_management'
)

tables = ["Admin", "Judge", "`Case`", "Hearing"]

output_files = {
    "Admin": "Admin.csv",
    "Judge": "Judge.csv",
    "Case": "Case.csv",
    "Hearing": "Hearing.csv"
}

for table in tables:

    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)

    clean_name = table.replace("`", "")

    df.to_csv(output_files.get(clean_name, clean_name + ".csv"), index=False)

    print(f"{clean_name} exported successfully")

conn.close()
print("All CSV files generated")