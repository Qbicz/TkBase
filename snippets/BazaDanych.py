import pyodbc

# Connect to the SqlLocalDb
con = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server=(localdb)\\MyInstance;Database=fkubicz;integrated security = true')

# Get a Cursor
cursor = con.cursor()

# Select some data
cursor.execute("SELECT id, first_name, last_name FROM emp")
#row = cursor.fetchone()
#print('name:', row[1])         # access by column index
#print('name:', row.last_name)  # or access by name

# fetchone returns None when all rows have been retrieved.
while 1:
    row = cursor.fetchone()
    if not row:
        break
    # print('id:', row.id)
    print(row.id, ':', row.first_name, row.last_name)

#cursor.tables()
#rows = cursor.fetchall()
#for row in rows:
#    print(row.table_name)

# If you are going to process the rows one at a time, you can use the cursor itself as an iterator:
cursor.execute("SELECT id, city FROM warehouse")
for row in cursor:
    print(row.id, row.city)
    
input('Twoja Kolej >> ')