from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time

doneTiles = []
mineField = []

def isGameOver():
    try:
        # Search for triggered bombs, return true if found
        browser.find_element_by_class_name('bombrevealed')
        return True
    except:
        try:
            # Search for blank spaces, return false if found
            browser.find_element_by_class_name('blank')
            return False

        except:
            # Otherwise, return true since game was won (no bombs, no blanks)
            return True

def processTile(tileElem, tileNum):
    numClicked = 0
    
    # Get tile location
    tileId = tileElem.get_attribute("id")

    # Check if already finished tile
    if tileId in doneTiles:
        print('Skipped ' + tileId )
        return numClicked

    location = [int(s) for s in tileId.split('_') if s.isdigit()]

    # Get surrounding tiles
    print(str(location) + ': Processing')
    adjTiles = getAdjacentTiles(location)

    # Check for obvious bombs or blanks
    numBlanks = 0
    numBombs = 0

    for adjTileElem in adjTiles:
        # Check if blank tile
        tileType = adjTileElem.get_attribute('class')
        if 'blank' in tileType or 'bombflagged' in tileType:
            numBlanks += 1
        if 'bombflagged' in tileType:
            numBombs += 1

    if numBlanks == tileNum:
        # Add to completed tiles list
        doneTiles.append(tileId)

        # Flag all blank neighbor tiles
        for adjTileElem in adjTiles:
            if 'blank' in adjTileElem.get_attribute('class'):
                # Right clicks tile to flag as bomb
                actionChains = ActionChains(browser)
                actionChains.context_click(adjTileElem).perform()
                numClicked += 1

    if numBombs == tileNum:
        # Add to completed tiles list
        doneTiles.append(tileId)

        # Click all blank neighbor tiles
        for adjTileElem in adjTiles:
            if 'blank' in adjTileElem.get_attribute('class'):
                # clicks obviously safe tile
                adjTileElem.click()
                numClicked += 1 + processTile(adjTileElem, int(adjTileElem.get_attribute("class")[-1]))


    print(str(location) + ': Done')
    return numClicked

def getAdjacentTiles(position):
    # initialize function/variables
    adjTiles = []

    # Dictionary of row/col modifiers based on adjacent tile you want
    positions = { "top-L": [-1, -1], "top-M": [-1,  0], "top-R": [-1,  1],
                  "mid-L": [ 0, -1],                    "mid-R": [ 0,  1],
                  "bot-L": [ 1, -1], "bot-M": [ 1,  0], "bot-R": [ 1,  1] }

    # Loop through each adjacent position
    for currentPos in positions:
        # Get row and column 
       row = positions[currentPos][0] + position[0]
       col = positions[currentPos][1] + position[1]

       # Check if valid row and column
       if row > 0 and row < 17 and col > 0 and col < 31:
           # Get webElement of the tile, indexed to account for 0-based offset of list
           currentElem = mineField[row - 1][col - 1]

           #Only add either blank or flag tiles
           tileType = currentElem.get_attribute('class')
           if 'bombflagged' in tileType or 'blank' in tileType:
               adjTiles.append(currentElem)

    # Return all adjacent tiles
    return adjTiles

# Create webdriver object for firefox browser
browser = webdriver.Firefox()

# Open browser to this page
browser.get('http://minesweeperonline.com/')

print('Getting field data ...')
for i in range(1, 17):
    mineField.append([])
    for j in range(1, 31):
        tileId = str(i) + '_' + str(j)
        mineField[i - 1].append(browser.find_element_by_id(tileId))
print('Done getting field data')

choice = ''

while not choice == 'quit':
    # Get top left tile element
    mineField[1][1].click()

    while not isGameOver():
        # Reset number of tiles clicked
        tilesClicked = 0

        # Loop through all numbered tile types
        for tileNum in range(1,9):
            # Get list of elements
            try:
                tileList = browser.find_elements_by_class_name('open' + str(tileNum))
                print( 'Number of ' + str(tileNum) + ' tiles: ' + str(len(tileList)))

                for i in range(len(tileList)):
                    tilesClicked += processTile(tileList[i], tileNum)
            except Exception as err:
                print('An exception happened: ' + str(err))

        # Check if no tiles were clicked
        print('Tiles Clicked: ' + str(tilesClicked))
        if tilesClicked == 0:
            print('Stuck')
            stuck = input()

    # Get user input
    doneTiles.clear()
    choice = input()
    time.sleep(2)