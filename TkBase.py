from tkinter import *
from tkinter import ttk
import pyodbc
root = Tk()

# State Variables
cnames = StringVar()
newEntry = StringVar()
updateEntry = StringVar()

# Functions
def getSelectedTable():
    selection = tablebox.curselection()
    return tablebox.get(selection[0])
    
    
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
    e = Entry(child, textvariable = newEntry, width=60)
    ok = ttk.Button(child, text = 'OK', command=writeNewRecord, default='active')
    
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
def writeNewRecord():
    print('writeRecord')
    
    print("newEntry: %r" % newEntry.get())
    # build a tuple from a modified state variable string
    newTuple = tuple(newEntry.get().split(' ; '))
    print(newTuple)
    
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
    
    elif gTable == 'emp': # add Inventory table
        pass
        
    else:
        print('TODO: Raise an exception here?')
    
    print(Query)
    cursor.execute(Query)
    

def updateRecord():
    print('updateRecord: ')
    child = Toplevel(c, takefocus=True) # child window
    child.wm_title("Modyfikacja wpisu w tabeli %s" % gTable)
    e = Entry(child, textvariable = updateEntry, width=60)
    ok = ttk.Button(child, text = 'OK', command=writeUpdateRecord, default='active')
    
    e.grid(column=1, row=1, sticky=W)
    ok.grid(column=2, row=1, sticky=W)
    e.focus_set()
    
    if not lbox.curselection():
        print('pop-up : nie zaznaczono rekordu do modyfikacji')
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
    
    
def writeUpdateRecord():
    print('writeUpdateRecord')
    
    print("updateEntry: %r" % updateEntry.get())
    # build a tuple from a modified state variable string
    updateTuple = tuple(updateEntry.get().split(' ; '))
    print(updateTuple)
     
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
        
    elif gTable == 'emp':
        pass
        
    print(Query)
    cursor.execute(Query)
  
# this function only shows warning, no editing possible
def deleteRecord():
    print('deleteRecord: ')
    popup = Toplevel(c, takefocus=True) # child window
    popup.wm_title("Usuwanie wpisu z tabeli %s" % gTable)
    popLabel = ttk.Label(popup, text="Czy na pewno chcesz usunąć ten wpis?")
    yesButton = ttk.Button(popup, text="Tak", command=writeDeleteRecord)
    noButton = ttk.Button(popup, text="Nie", command=lambda: closePopup(popup), default='active')
    
    popLabel.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
    yesButton.grid(column=0, row=1)
    noButton.grid(column=1, row=1)

    if not lbox.curselection():
        print('pop-up : nie zaznaczono rekordu do modyfikacji')
        return
     
    # get the selected record id       
    selection = lbox.curselection()
    recordString = lbox.get(selection[0])
    print('%r' % recordString)
    ID = recordString.split(' ; ')[-1] # ID is after ; in listbox
    print('%r' % ID)
  
def writeDeleteRecord():
    pass
    
def closePopup(popup):
    popup.destroy()
  
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
        
    elif gTable== 'Gitary':
        cursor.execute('SELECT ID, producent, model, data FROM Gitary')
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            dbRows.append(row.producent + ' ' + row.model + ' ; ' + str(row.ID))
    
    
    
    cnames.set(dbRows)
    return dbRows

    
# Called when the selection in the listbox changes; figure out
# which country is currently selected, and then lookup its country
# code, and from that, its population.  Update the status message
# with the new population.  As well, clear the message about the
# gift being sent, so it doesn't stick around after we start doing
# other things.
def showPopulation(*args):
    idxs = lbox.curselection()
    if len(idxs)==1:
        idx = int(idxs[0])
        print('idx: ', idx)
        code = countrycodes[idx]
        name = countrynames[idx]
        popn = populations[code]
        statusmsg.set("The population of %s (%s) is %d" % (name, code, popn))
    sentmsg.set('')

# Called when the user double clicks an item in the listbox, presses
# the "Send Gift" button, or presses the Return key.  In case the selected
# item is scrolled out of view, make sure it is visible.
#
# Figure out which country is selected, which gift is selected with the 
# radiobuttons, "send the gift", and provide feedback that it was sent.
def sendGift(*args):
    idxs = lbox.curselection()
    if len(idxs)==1:
        idx = int(idxs[0])
        lbox.see(idx)
        name = countrynames[idx]
        # Gift sending left as an exercise to the reader
        sentmsg.set("Sent %s to leader of %s" % (gifts[gift.get()], name))

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
chooseTable = ['Magazyny', 'Gitary', 'emp']
selectedTable = chooseTable[0]

dbRows = []
    

    
# ----- Tkinter part -------

# Initialize our country "databases":
#  - the list of country codes (a subset anyway)
#  - a parallel list of country names, in the same order as the country codes
#  - a hash table mapping country code to population<
countrycodes = ('ar', 'au', 'be', 'br', 'ca', 'cn', 'dk', 'fi', 'fr', 'gr', 'in', 'it', 'jp', 'mx', 'nl', 'no', 'es', 'se', 'ch')
countrynames = ('Argentina', 'Australia', 'Belgium', 'Brazil', 'Canada', 'China', 'Denmark', \
        'Finland', 'France', 'Greece', 'India', 'Italy', 'Japan', 'Mexico', 'Netherlands', 'Norway', 'Spain', \
        'Sweden', 'Switzerland')
#cnames = StringVar(value=countrynames)

populations = {'ar':41000000, 'au':21179211, 'be':10584534, 'br':185971537, \
        'ca':33148682, 'cn':1323128240, 'dk':5457415, 'fi':5302000, 'fr':64102140, 'gr':11147000, \
        'in':1131043000, 'it':59206382, 'jp':127718000, 'mx':106535000, 'nl':16402414, \
        'no':4738085, 'es':45116894, 'se':9174082, 'ch':7508700}

# Names of the gifts we can send
gifts = { 'card':'Greeting card', 'flowers':'Flowers', 'nastygram':'Nastygram'}

# State variables
gift = StringVar()
sentmsg = StringVar()
statusmsg = StringVar()
searchText = StringVar()

tablenames = StringVar(value=chooseTable)

        
# Create and grid the outer content frame
c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

# Create the different widgets; note the variables that many
# of them are bound to, as well as the button callback.
# Note we're using the StringVar() 'cnames', constructed from 'countrynames'
tablelabel = ttk.Label(c, text='Tabele')
tablebox = Listbox(c, listvariable=tablenames)
rowlabel = ttk.Label(c, text='Wyniki')
lbox = Listbox(c, listvariable=cnames, height=5)
lbl = ttk.Label(c, text="Send to country's leader:")
g1 = ttk.Radiobutton(c, text=gifts['card'], variable=gift, value='card')
g2 = ttk.Radiobutton(c, text=gifts['flowers'], variable=gift, value='flowers')
g3 = ttk.Radiobutton(c, text=gifts['nastygram'], variable=gift, value='nastygram')
send = ttk.Button(c, text='Send Gift', command=sendGift, default='active')
sentlbl = ttk.Label(c, textvariable=sentmsg, anchor='center')
status = ttk.Label(c, textvariable=statusmsg, anchor=W)
searchLabel = ttk.Label(c, text='Wyszukaj w tablicy')
searchbar = ttk.Entry(c, textvariable = searchText)
searchText.set("np. Gibson")
b = ttk.Button(c, text="Szukaj", width=10, command=getSearchText)
newButton = ttk.Button(c, text="Dodaj nowy", command=newRecord, default='active')
updateButton = ttk.Button(c, text="Modyfikuj", command=updateRecord, default='active')
deleteButton = ttk.Button(c, text="Usuń", command=deleteRecord, default='active')

# Grid all the widgets
tablelabel.grid(column=0,row=0,pady=5)
tablebox.grid(column=0,row=1, rowspan=5, padx=10, sticky=(N,S,E,W))
lbox.grid(column=1, row=1, rowspan=5, columnspan=2, sticky=(N,S,E,W)) # add a widget to column 2
rowlabel.grid(column=1,row=0,pady=5)
lbl.grid(column=3, row=0, padx=10, pady=5)
g1.grid(column=3, row=1, sticky=W, padx=20)
g2.grid(column=3, row=2, sticky=W, padx=20)
g3.grid(column=3, row=3, sticky=W, padx=20)
send.grid(column=3, row=6, sticky=(W,E))
sentlbl.grid(column=3, row=5, columnspan=2, sticky=N, pady=5, padx=5)
status.grid(column=2, row=6, columnspan=2, sticky=(W,E))
searchLabel.grid(column=4, row=0, sticky=(N,S,E,W))
searchbar.grid(column=4, row=1, sticky=W)
newButton.grid(column=4, row=4, padx=5, pady=5)
updateButton.grid(column=4, row=5, padx=5, pady=5)
deleteButton.grid(column=4, row=6, padx=5, pady=5)

b.grid(column=5, row=1, sticky=W)
c.grid_columnconfigure(0, weight=1)
c.grid_rowconfigure(5, weight=1)

# Set event bindings for when the selection in the listbox changes,
# when the user double clicks the list, and when they hit the Return key
lbox.bind('<<ListboxSelect>>', showPopulation)
lbox.bind('<Double-1>', sendGift)
root.bind('<Return>', sendGift)
tablebox.bind('<<ListboxSelect>>', showRowsFromTable)

# Colorize alternating lines of the listbox
for i in range(0,len(dbRows),2):
    lbox.itemconfigure(i, background='#f0f0ff')

# Set the starting state of the interface, including selecting the
# default gift to send, and clearing the messages.  Select the first
# country in the list; because the <<ListboxSelect>> event is only
# generated when the user makes a change, we explicitly call showPopulation.
gift.set('card')
sentmsg.set('')
statusmsg.set('')
lbox.selection_set(0)
tablebox.selection_set(0)
# global var gTable
gTable = getSelectedTable()

#searchbar.insert('1.0', 'np. Gibson')

# on event
#searchText = searchbar.get('1.0', 'end')

showPopulation()
#showRowsFromTable()

root.wm_title('TkBase - Zarządzaj swoją bazą danych')
root.mainloop()