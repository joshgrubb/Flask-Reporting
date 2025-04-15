import pandas as pd
import pyodbc

# Connect to SQL Server (adjust connection string as needed)
conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=TOC-CW-SVR-01;"
    "Database=CW;"
    "Trusted_Connection=yes;"
)

# Read data from the source table
query = "SELECT * FROM [azteca].[INSPQUESTION]"
df = pd.read_sql(query, conn)

# Clean up the 'ANSWER' column: replace specific strings with NaN, then convert to numeric.
df["ANSWER"] = pd.to_numeric(
    df["ANSWER"].replace({"NA": None, "na": None, "N/A": None}), errors="coerce"
)

# Drop rows where conversion to numeric failed (i.e., where ANSWER is NaN)
df_clean = df.dropna(subset=["ANSWER"])

# Pivot the table so that each distinct QUESTION becomes its own column with aggregated ANSWERs.
# Here, assuming there's a grouping identifier; if not, you might create one.
# In this example, we'll assume you want a single row pivot (aggregating all data)
pivot_df = df_clean.pivot_table(
    index=["INSPQUESTIONID"],  # Group by Inspection Question ID
    columns="QUESTION",
    values="ANSWER",
    aggfunc="sum",
).reset_index(drop=True)

# Display the resulting pivoted DataFrame
print(pivot_df)
