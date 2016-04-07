from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import pyodbc
root = Tk()

# State Variables
cnames = StringVar()
newEntry = StringVar()
updateEntry = StringVar()
deleteEntry = StringVar()
Mode = StringVar() # user, admin or developer mode

# Functions
def getSelectedTable():
    selection = tablebox.curselection()
    try:
        return tablebox.get(selection[0])
    except IndexError:
        print('Tabela nie jest zaznaczona, wyswietlam stara.')
        return gTable
    
    
def updateSelectedTable():
    global gTable
    gTable = getSelectedTable()
    
    
def removeFirstTupleElem(originalTuple):
    newList = list(originalTuple)
    del newList[0]
    return tuple(newList)
    
# function opens new window and passes user input to newEntry StringVar
def newRecord():
    print('New record: ')
    # child window
    child = Toplevel(c, takefocus=True)
    child.wm_title("Nowy wpis w tabeli %s" % gTable)
    e = Entry(child, textvariable = newEntry, width=70)
    ok = ttk.Button(child, text = 'OK', command=lambda: writeNewRecord(child), default='active')
    
    e.grid(column=1, row=1, sticky=W)
    ok.grid(column=2, row=1, sticky=W)
    e.focus_set()
    
    # Show tables' columns default text
    print('selected table:%r' % gTable)
    # parametrizing doesn't work -> build string in python
    cursor.execute('SELECT * FROM %s WHERE ID = 1' % gTable)
    tupleString = cursor.fetchone()
    print(tupleString)
    #listString = list(tupleString) # convert to list 
    exampleString = ' ; '.join(str(x) for x in tupleString[1:]) # take subset without ID
    
    # save to state variable
    newEntry.set(exampleString)
    print("exampleString: %r" % exampleString)
    
    

# function splits the string from user and sends it to database with SQL
def writeNewRecord(toplevel):
    print('writeRecord')
    
    print("newEntry: %r" % newEntry.get())
    # build a tuple from a modified state variable string
    newTuple = tuple(newEntry.get().split(' ; '))
    print(newTuple)
    
    # Validation
    elements = len(newTuple)
    if elements != validElements[gTable]:
        messagebox.showwarning("Walidacja negatywna", "Poprawnie uzupełnij tabelę")
        toplevel.destroy()
        return
    
    # TODO: use dictionary as switch instead of if-else chain
    # http://code.activestate.com/recipes/181064/
    
    # delete ID, the first element of a tuple
    # better - remove ID before ''.join in newRecord
    #newTuple = removeFirstTupleElem(myTuple)
    
    # add newEntry to the database, to selected table
    if gTable == 'Magazyny':
    
        Query = """
        INSERT INTO Magazyny (miasto, adres, kraj, telefon)
                VALUES(%r, %r, %r, %r) """ % (newTuple)
                
    elif gTable == 'Gitary':
        Query = """
        INSERT INTO Gitary (producent, model, data, cena)
                VALUES(%r, %r, %r, %r) """ % (newTuple)
    
    elif gTable == 'StanMagazynowy':
        pass
        
    else:
        print('TODO: Raise an exception here?')
    
    print(Query)
    cursor.execute(Query)
    toplevel.destroy()
    showRowsFromTable()
    

def updateRecord():
    print('updateRecord: ')
    child = Toplevel(c, takefocus=True) # child window
    child.wm_title("Modyfikacja wpisu w tabeli %s" % gTable)
    e = Entry(child, textvariable = updateEntry, width=70)
    ok = ttk.Button(child, text = 'OK', command=lambda: writeUpdateRecord(child), default='active') # refactor to class with self.updateWindow
    
    e.grid(column=1, row=1, sticky=W)
    ok.grid(column=2, row=1, sticky=W)
    e.focus_set()
    
    if not lbox.curselection():
        print('pop-up : nie zaznaczono rekordu do modyfikacji')
        messagebox.showwarning(
            "Modyfikacja rekordu",
            "Nie zaznaczono rekordu do modyfikacji"
        )
        child.destroy()
        return
     
    # get the selected record id       
    selection = lbox.curselection()
    recordString = lbox.get(selection[0])
    print('%r' % recordString)
    ID = recordString.split(' ; ')[-1] # ID is after ; in listbox
    print('%r' % ID)
    
    cursor.execute('SELECT * FROM %s WHERE ID = %s' % (gTable, ID))
    tupleString = cursor.fetchone()
    updateString = ' ; '.join(str(x) for x in tupleString[1:]) # take subset without ID
    
    # save to state variable and add ID information
    updateEntry.set(updateString + ' ; ' + ID)
    print("updateString: %r" % updateString)
    
    
def writeUpdateRecord(toplevel):
    print('writeUpdateRecord')
    
    print("updateEntry: %r" % updateEntry.get())
    # build a tuple from a modified state variable string
    updateTuple = tuple(updateEntry.get().split(' ; '))
    print(updateTuple)
    
    # Validation
    elements = len(updateTuple)
    if elements != validElements[gTable]:
        messagebox.showwarning("Walidacja negatywna", "Poprawnie uzupełnij tabelę")
        return
        
     
    if gTable == 'Magazyny':
        
        Query = """
        UPDATE Magazyny
        SET miasto=%r,adres=%r, kraj=%r, telefon=%r 
        WHERE ID = %s; """ % (updateTuple)
        
    elif gTable == 'Gitary':
    
        Query = """
        UPDATE Gitary
        SET producent=%r, model=%r, data=%r, cena=%r
        WHERE ID = %s; """ % (updateTuple)
        
    elif gTable == 'StanMagazynowy':
        pass
        
    print(Query)
    cursor.execute(Query)
    toplevel.destroy()
    showRowsFromTable()
    
  
# this function only shows warning, no editing possible
def deleteRecord():
    print('deleteRecord: ')
    popup = Toplevel(c, takefocus=True) # child window
    popup.wm_title("Usuwanie wpisu z tabeli %s" % gTable)
    popLabel = ttk.Label(popup, text="Czy na pewno chcesz usunąć ten wpis?")
    yesButton = ttk.Button(popup, text="Tak", command=lambda: writeDeleteRecord(ID))
    noButton = ttk.Button(popup, text="Nie", command=lambda: closePopup(popup), default='active')
    
    popLabel.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
    yesButton.grid(column=0, row=1)
    noButton.grid(column=1, row=1)

    if not lbox.curselection():
        print('pop-up : nie zaznaczono rekordu do modyfikacji')
        messagebox.showwarning(
            "Usuwanie rekordu",
            "Nie zaznaczono rekordu do usunięcia"
        )
        return
     
    # get the selected record id       
    selection = lbox.curselection()
    recordString = lbox.get(selection[0])
    print('%r' % recordString)
    ID = recordString.split(' ; ')[-1] # ID is after ; in listbox
    print('%r' % ID)
    
    deleteID.set(updateString + ' ; ' + ID)
    print("updateString: %r" % updateString)
  
def writeDeleteRecord(ID):
    print("deleteEntry")
        
    Query = """
    DELETE FROM %s
    WHERE ID = %s; """ % (gTable, ID)
        
    print(Query)
    cursor.execute(Query)
    showRowsFromTable()
    
    
def closePopup(popup):
    popup.destroy()
  
def switchAdminMode(newMode):
    print('switchAdminMode()')
    
    if newMode == Mode:
        pass
    elif newMode == 'devel':
        print('> devel mode')
    elif newMode == 'admin':
        print('> admin mode')
    elif newMode == 'user':
        print('> user mode')
        
  
def showRowsFromTable(*args):
    print('showRowsFromTable()')
    dbRows = [] # istnieje tylko wewnatrz funkcji
    updateSelectedTable()
    
    # optional args - leave it here as an example of event.widget
    """
    for event in args:
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        print('selection: ', selection, ': ', value)
    """
    
    if gTable == 'Magazyny':
        cursor.execute('SELECT ID, miasto, adres FROM Magazyny')
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            # construct a list for showing in Tk Listbox
            dbRows.append(row.miasto + ', ' + row.adres + ' ; ' + str(row.ID)) # ID imported for update/delete functions
        
    elif gTable == 'Gitary':
        cursor.execute('SELECT ID, producent, model, data FROM Gitary')
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            dbRows.append(row.producent + ' ' + row.model + ' ; ' + str(row.ID))
    
    elif gTable == 'StanMagazynowy':
        print('showRows - StanMagazynowy')
        cursor.execute('SELECT ID, IDproduktu, IDmagazynu, ilosc FROM StanMagazynowy')
        # JOIN
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            dbRows.append(row.IDproduktu + ' ' + row.IDmagazynu + ' ; ' + str(row.ID))
    
    cnames.set(dbRows)
    return dbRows


def showRowInfo(*args):
    print('showRowInfo')
    # here put info about current record
    
def getSearchText(*args):
    print(searchText.get())
    
    
"""
MAIN
- maybe refactor later to

if __name__ == "__main__":
    main()
"""    

# Connect to the SqlLocalDb
con = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server=(localdb)\\MyInstance;Database=fkubicz;integrated security = true')
# commit transactions after each query
con.autocommit = True

# Get a Cursor
cursor = con.cursor()

# Select some data
chooseTable = ['Magazyny', 'Gitary', 'StanMagazynowy']
selectedTable = chooseTable[0]

dbRows = []
    

    
# ----- Tkinter part -------

# State variables
searchText = StringVar()
tablenames = StringVar(value=chooseTable)
        
# Create and grid the outer content frame
c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

# Create the different widgets; note the variables that many
# of them are bound to, as well as the button callback.
tablelabel = ttk.Label(c, text='Tabele')
tablebox = Listbox(c, listvariable=tablenames)
rowlabel = ttk.Label(c, text='Wyniki')
lbox = Listbox(c, listvariable=cnames, height=5)
searchLabel = ttk.Label(c, text='Wyszukiwanie w tablicy')
searchbar = ttk.Entry(c, textvariable = searchText)
searchText.set("np. Gibson")
b = ttk.Button(c, text="Szukaj", width=10, command=getSearchText)
modificationsLabel = ttk.Label(c, text='Modyfikacje tablicy')
newButton = ttk.Button(c, text="Dodaj nowy", command=newRecord, default='active')
updateButton = ttk.Button(c, text="Modyfikuj", command=updateRecord, default='active')
deleteButton = ttk.Button(c, text="Usuń", command=deleteRecord, default='active')
#modeLabel = ttk.Label(c, text="Wybór trybu")
userButton = ttk.Button(c, text="Tryb użytkownika", command=lambda: switchAdminMode('user'), default='active')
adminButton = ttk.Button(c, text="Tryb administratora", command=lambda: switchAdminMode('admin'), default='active')
develButton = ttk.Button(c, text="Tryb developera", command=lambda: switchAdminMode('devel'), default='active')

# Grid all the widgets
tablelabel.grid(column=0,row=0, padx=5, pady=5, sticky=(N,S,E,W))
tablebox.grid(column=0,row=1, rowspan=6, padx=5, sticky=(N,S,E,W))
lbox.grid(column=1, row=1, rowspan=6, columnspan=4, sticky=(N,S,E,W)) # add a widget to column 2
rowlabel.grid(column=1,row=0,pady=5)
searchLabel.grid(column=6, row=0, sticky=(N,S,E,W))
searchbar.grid(column=6, row=1, sticky=W)
modificationsLabel.grid(column=6, row=3, pady=5, sticky=(N,S,E,W))
newButton.grid(column=6, row=4, padx=5, pady=0)
updateButton.grid(column=6, row=5, padx=5, pady=0)
deleteButton.grid(column=6, row=6, padx=5, pady=0)
#modeLabel.grid(column=0, row=8, pady=5)
userButton.grid(column=1, row=8)
adminButton.grid(column=2, row=8)
develButton.grid(column=3, row=8)

lbox
b.grid(column=5, row=1, sticky=W)
c.grid_columnconfigure(0, weight=1)
c.grid_rowconfigure(5, weight=1)

# Set event bindings for when the selection in the listbox changes,
# when the user double clicks the list, and when they hit the Return key
lbox.bind('<<ListboxSelect>>', showRowInfo)
#lbox.bind('<Double-1>', sendGift)
#root.bind('<Return>', sendGift)
tablebox.bind('<<ListboxSelect>>', showRowsFromTable)

# Colorize alternating lines of the listbox
for i in range(0,len(dbRows),2):
    lbox.itemconfigure(i, background='#f0f0ff')

lbox.selection_set(0)
tablebox.selection_set(0)
# global var gTable
gTable = getSelectedTable()
# valid number of elements for each table
validElements = {'Magazyny': 5, 'Gitary': 5, 'StanMagazynowy': 6}

#searchbar.insert('1.0', 'np. Gibson')

# on event
#searchText = searchbar.get('1.0', 'end')

showRowsFromTable()

root.wm_title('TkBase - Zarządzaj swoją bazą danych')
root.mainloop()