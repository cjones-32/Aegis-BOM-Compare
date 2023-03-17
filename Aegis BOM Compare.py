import csv
import os
import re

def loadBOM(BOMpath):
    # Dictionary to store the BOM, ref des is Key, PN is Value
    BOM = {}
    with open(BOMpath) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Ignore first row
            if row[0] != 'Designator':
                # Verify there is not a duplicate designator
                if row[0] in BOM:
                    print(f'\nCAUTION! DUPLICATE DESIGNATORS! {row[0]}\n')
                    BOM[row[0]]=BOM[row[0]] + ', ' + row[1]
                # Add next part to BOM
                else:
                    BOM[row[0]]=row[1]
    return(BOM)

def compareBOMs(newBOM, oldBOM):
    # Will store changes, additions, and removals
    changes = []
    # Stores the total count for part numbers
    count = {}
    # Work through the new BOM to find changes/additions
    for refdes, comp in newBOM.items():
        # Add to the total part number count
        if comp in count:
            count[comp]=count[comp] + 1
        else:
            count[comp]=1
        # Part is in both BOMs
        if refdes in oldBOM:
            # Part changed
            if newBOM[refdes] != oldBOM[refdes]:
                changes.append({'refdes'   : refdes,
                                'state'    : 'changed',
                                'oldPN'    : oldBOM[refdes],
                                'newPN'    : newBOM[refdes],
                                'newPNqty' : 0,
                                'oldPNqty' : 0})
        # Part added
        else:
            changes.append({'refdes' : refdes,
                            'state'    : 'added',
                            'oldPN'    : 'DNI',
                            'newPN'    : newBOM[refdes],
                            'newPNqty' : 0,
                            'oldPNqty' : 0})
    # Check old BOM for now DNI parts
    for refdes in oldBOM:
        # Part made DNI
        if refdes not in newBOM:
            changes.append({'refdes' : refdes,
                            'state'    : 'removed',
                            'oldPN'    : oldBOM[refdes],
                            'newPN'    : 'DNI',
                            'newPNqty' : 0,
                            'oldPNqty' : 0})
    # Update new counts
    for change in changes:
        if change['newPN'] in count:
            change['newPNqty'] = count[change['newPN']]
        if change['oldPN'] in count:
            change['oldPNqty'] = count[change['oldPN']]
    # Output the changes
    outputChanges(changes)

def outputChanges(changes):
    changedParts = []
    addedParts = []
    removedParts = []
    # Record all possible part change combinations into prospective arrays
    for change in changes:
        if change['state'] == 'changed':
            if change['newPN'] + ' - ' + change['oldPN'] not in changedParts:
                changedParts.append(change['newPN'] + ' - ' + change['oldPN'])
        if change['state'] == 'added':
            if change['newPN'] not in addedParts:
                addedParts.append(change['newPN'])
        if change['state'] == 'removed':
            if change['oldPN'] not in removedParts:
                removedParts.append(change['oldPN'])
    # Print all the changes
    if not changes:
        print('No changes detected!')
    # Print component changes
    for combo in changedParts:
        print('\to   Replace', end='')
        comma = False
        for change in changes:
            if change['newPN'] + ' - ' + change['oldPN'] == combo:
                description = f'\n\t\t▪   {change["oldPN"]} (new qty {change["oldPNqty"]})\n\t\t▪   {change["newPN"]} (new qty {change["newPNqty"]})'
                if comma is True:
                    print(',',end='')
                print(' ' + change['refdes'], end='')
                comma = True
        print(description)
    # Print added parts
    for part in addedParts:
        print('\to   Add', end='')
        comma = False
        for change in changes:
            if change['newPN'] == part:
                description = f'\n\t\t▪   {change["newPN"]} (new qty {change["newPNqty"]})'
                if comma is True:
                    print(',',end='')
                print(' ' + change['refdes'], end='')
                comma = True
        print(description)
    # Print DNI parts
    for DNI in removedParts:
        print('\to   DNI', end='')
        comma = False
        for change in changes:
            if change['oldPN'] == DNI:
                description = f'\n\t\t▪   {change["oldPN"]} (new qty {change["oldPNqty"]})'
                if comma is True:
                    print(',',end='')
                print(' ' + change['refdes'], end='')
                comma = True
        print(description)
    userInput = input()
    if userInput == 'swap':
        findBOMs(True)
    elif userInput == 'normal':
        findBOMs(False)
        

def askLinks():
    newBOMpath = input('Enter path to new Aegis BOM: ').strip('" ')
    newBOM = loadBOM(newBOMpath)
    oldBOMpath = input('Enter path to old Aegis BOM: ').strip('" ')
    oldBOM = loadBOM(oldBOMpath)
    assyName = newBOMpath.split("Sync_")[1][:9]
    assyRev = newBOMpath[-7:-4]
    showExtraFiles(assyName, assyRev)
    print(f'✤   BOM changes (from {os.path.basename(oldBOMpath.split("Sync_")[1].split(".")[0])} to {os.path.basename(newBOMpath.split("Sync_")[1].split(".")[0])}):')
    compareBOMs(newBOM, oldBOM)

# Swap is bool for if the newest file needs to be swapped for most recent rev
def findBOMs(swap):
    files = []
    date = 0
    assyName = ''
    assyRev = ''
    # Verify there are only two BOMs in the folder with the script
    if len(os.listdir(os.getcwd())) == 3:
        for file in os.listdir(os.getcwd()):
            if not re.search('\.py$', file, re.IGNORECASE):
                # Enter the files in order of date
                if os.path.getmtime(file) < date:
                    if swap == False:
                        files.append(file)
                    else:
                        files.insert(0, file)
                else:
                    if swap == False:
                        files.insert(0, file)
                    else:
                        files.append(file)
                date = os.path.getmtime(file)
        # Continue on with files found
        newBOM = loadBOM(f'{os.getcwd()}\\{files[0]}')
        oldBOM = loadBOM(f'{os.getcwd()}\\{files[1]}')
        assyName = files[0].split("Sync_")[1][:9]
        assyRev = files[0][-7:-4]
        showExtraFiles(assyName, assyRev)
        
        print(f'✤   BOM changes (from {files[1].split("Sync_")[1].split(".")[0]} to {files[0].split("Sync_")[1].split(".")[0]}):')
        compareBOMs(newBOM, oldBOM)
    else:
        print('Error: Expecting 2 BOMs in a folder with the script. Entering Manual Mode')
        askLinks()

def showExtraFiles(assyName, assyRev):
    print(f'•   Specification Drawing {assyName[:5]}B46{assyName[7:9]}{assyRev}.pdf\n')
    print(f'•   Assembly/Schematic Drawing {assyName}{assyRev}.pdf')
    print(f'•   {assyName}{assyRev} SAP Import File.xlsx')
    
findBOMs(False)
