import psycopg2
from psycopg2 import sql

def create_table():
    # Database connection parameters
    db_params = {
        'dbname': 'your_dbname',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'localhost',  # Change if your PostgreSQL is hosted elsewhere
        'port': '5432'        # Default PostgreSQL port
    }

    # Establish the connection to the database
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Corrected SQL command to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id int,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            age INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        # Execute the command to create the table
        cursor.execute(create_table_query)
        conn.commit()

        print("Table created successfully!")



        # Insert sample data into the table
        insert_query = '''
        INSERT INTO users (name, email, age)
        VALUES
            ('Alice Johnson', 'alice@example.com', 25),
            ('Bob Smith', 'bob@example.com', 30),
            ('Charlie Brown', 'charlie@example.com', 22);
        '''
        cursor.execute(insert_query)
        conn.commit()
        print("Sample data inserted successfully!")


    except Exception as error:
        print(f"Error creating table: {error}")
    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_table()
