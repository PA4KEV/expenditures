import sys
import mysql.connector
from datetime import datetime

# Check if a year is provided as a command line argument
if len(sys.argv) < 2:
    print("Please provide a year as a command line argument.")
    sys.exit(1)

# Extract the year from the command line argument
year = sys.argv[1]

# Construct the file name using the provided year
csv_file = f"expenditures_{year}"

try:
    # Read CSV data from file
    with open(csv_file, 'r') as file:
        csv_row = file.read().strip()
except FileNotFoundError:
    print(f"File '{csv_file}' not found.")
    sys.exit(1)

# Connect to MySQL
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='zairyo',
    port="33066",
    database='expenses'
)
cursor = db.cursor()

# Create the categories table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(255) UNIQUE
    )
''')

# Create the expenses table for the given year
table_name = f"expenses{year}"
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT,
        description VARCHAR(255),
        price FLOAT,
        date DATE,
        time TIME,
        location VARCHAR(255),
        method VARCHAR(255),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
''')

# Prepare data for insertion into the expenses table
rows = csv_row.split(';')
expenses_data = []

for row in rows:
    values = row.split(',')
    
    if len(values) < 7:
        print(f"Skipping row with insufficient values: {row}")
        continue
    
    category_value = values[0].strip()
    description = values[1].strip()
    price = float(values[2]) if values[2] else None
    date_str = values[3].strip()
    time = values[4].strip()
    location = values[5].strip()
    method = values[6].strip()
    
    if not category_value:
        print(f"Skipping row with invalid category value: {row}")
        continue
    
    # Check if the category already exists in the categories table
    cursor.execute('SELECT id FROM categories WHERE category_name = %s', (category_value,))
    result = cursor.fetchone()
    
    if result is None:  # Category does not exist, create a new entry
        cursor.execute('INSERT INTO categories (category_name) VALUES (%s)', (category_value,))
        category_id = cursor.lastrowid
    else:
        category_id = result[0]
    
    # Parse and convert date string to the appropriate format
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"Skipping row with invalid date format: {row}")
        continue
    
# Parse and validate the time string in 24-hour format
    try:
        time_obj = datetime.strptime(time, "%H:%M").time()
    except ValueError:
        print(f"Invalid time format, using default value '00:00': {time}")
        time_obj = datetime.strptime("00:00", "%H:%M").time()

    expenses_data.append((
        category_id,
        description,
        price,
        date,
        time_obj,
        location,
        method
    ))

# Insert data into the expenses table
cursor.executemany(f'''
    INSERT INTO {table_name}
    (category_id, description, price, date, time, location, method)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
''', expenses_data)
db.commit()

# Close the database connection
cursor.close()
db.close()