import psycopg2
import sys

# Define the connection parameters
host = "127.0.0.1"
database = "your_database"
user = "your_user"
password = "your_password"

try:
    # Establish connection to the PostgreSQL database
    print("Connecting to the database...")
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    print("Connection successful!")

    # Create a cursor object using the connection
    cursor = conn.cursor()

    # Execute a query to see if the connection is working
    print("Executing query: SELECT * FROM your_table")
    cursor.execute("SELECT * FROM your_table")

    # Fetch all rows from the last executed statement
    rows = cursor.fetchall()

    # Check if any rows were returned
    if rows:
        print("Data fetched from your_table:")
        for row in rows:
            print(row)
    else:
        print("No data found in your_table.")

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    print("Connection closed.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
