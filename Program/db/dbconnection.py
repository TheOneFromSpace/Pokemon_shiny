import pyodbc


def get_db_connection():
    """Bulletproof SQL Server connection with Windows Authentication"""
    # Using the exact driver name from your list
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=PokemonShiny;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'  # Disable encryption for testing
    )

    print(f"Using connection string: {connection_string}")  # Debug output

    try:
        conn = pyodbc.connect(connection_string)
        print("Connection successful!")
        return conn
    except pyodbc.Error as e:
        print(f"CONNECTION FAILED: {str(e)}")
        print("Troubleshooting tips:")
        print("1. Verify SQL Server is running")
        print("2. Check firewall allows port 1433")
        print("3. Try 'SERVER=127.0.0.1' instead of 'localhost'")
        raise