import pyodbc

# Connect using ODBC
conn = pyodbc.connect(
    "DRIVER={PostgreSQL};"
    "SERVER=localhost;"
    "PORT=5432;"
    "DATABASE=testdb;"
    "UID=postgres;"
    "PWD=password;"
)

cursor = conn.cursor()

# Step 1: Create a table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    );
""")
conn.commit()

# Step 2: Insert sample data
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))
conn.commit()

# Step 3: Query data
cursor.execute("SELECT id, name, email FROM users")
rows = cursor.fetchall()

# Step 4: Print results
for row in rows:
    print(f"ID: {row.id}, Name: {row.name}, Email: {row.email}")

# Cleanup
cursor.close()
conn.close()
