import json
import csv
import requests
import sys
from lxml import html

with open('config.json', 'r') as f:
    config = json.load(f)

filename = config['dataFile']
savefile = config['saveFile']
data = config['dataColumns']
newDataNames = config['saveDataColumns']
maxamount = config['matchNumber']

dataIndices = []
matches = [newDataNames]

# Loading data
with open(filename, 'r') as f:
    print('Reading...')

    reader = csv.reader(f)
    index = 0

    for row in reader:
        if index == 0:
            dataIndices = [row.index(d) for d in data]

        else:
            match = []
            match = [row[dataIndex] for dataIndex in dataIndices]

            matches.append(match)

        index += 1

        if maxamount > -1 and index > maxamount:
            break

# Writing minimised data
with open(savefile, 'w') as f:
    print('Writing...')

    writer = csv.writer(f)

    for match in matches:
        writer.writerow(match)

print(f'Processed {len(matches) - 1} matches.\n')

# Get players' stats
datafile = config['saveFile']

def stats(team_name):
    base_url = 'https://sofifa.com'

    search_url = base_url + '/teams?keyword=' + team_name

    # Search page
    page = requests.get(search_url)
    tree = html.fromstring(page.content)

    expression = '//div[contains(@class, \'col-name\') and contains(@class, \'text-ellipsis\') and contains(@class, \'rtl\')]/a/text()'
    elements = tree.xpath(expression)
    selectedIndex = 0

    if len(elements) > 2:
        for i in range(int(len(elements) / 2)):
            print(f'[{i}]: ', elements[i * 2], '←', elements[i * 2 + 1])

        selectedIndex = int(input(f'Specify a club [0-{int(len(elements) / 2) - 1}]: ')) * 2
        print()

    elif len(elements) < 2:
        return None

    selected = (elements[selectedIndex], elements[selectedIndex + 1])
    print(f'\'{selected[0]} ← {selected[1]}\'')

    expression = '//div[contains(@class, \'col-name\') and contains(@class, \'text-ellipsis\') and contains(@class, \'rtl\')]/a/@href'
    team_url = base_url + tree.xpath(expression)[selectedIndex]

    # Team page
    page = requests.get(team_url)
    tree = html.fromstring(page.content)

    # Names
    expression = '//div[@class=\'lineup\']/div[@class=\'field-player\']/a/@title'
    lineup = tree.xpath(expression)
    lineup.reverse()

    # URLs
    expression = '//div[@class=\'lineup\']/div[@class=\'field-player\']/a/@href'
    player_urls = tree.xpath(expression)
    player_urls.reverse()

    players = {}

    for i in range(len(lineup)):
        players[lineup[i]] = base_url + player_urls[i]

    ret = {}

    for player_name, player_url in players.items():
        player_stats = []

        # Player page
        page = requests.get(player_url)
        tree = html.fromstring(page.content)

        # URLs
        expression = '//div[contains(@class, \'mb-2\') and contains(@class, \'mt-2\')]/div[contains(@class, \'column\') and contains(@class, \'col-4\')]/div'
        divs = tree.xpath(expression)
        expression = '//div[@class=\'mb-2\']/div[contains(@class, \'column\') and contains(@class, \'col-4\')]/div'
        divs.extend(tree.xpath(expression))

        for div in divs[:7]:
            expression = './/ul/li/span[contains(@class, \'label\')]/text()'
            stats = div.xpath(expression)

            player_stats.append(sum([int(x) for x in stats]) / len(stats))

            ret[player_name] = player_stats
        
    return ret

def hasKey(dictionary, key):
    for k, v in dictionary.items():
        if k == key:
            return True
    return False

def loadData(filename):
    # Home team wins →  [1 0 0]
    # Draw →            [0 1 0]
    # Away team wins →  [0 0 1]

    teams = {}

    X = []
    y = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        index = -1

        for row in reader:
            index += 1

            if index == 0:
                continue

            x = []

            if hasKey(teams, row[0]) == False:
                sys.stdout.write(f'Downloading team: {row[0]}... ')

                team_stats = stats(row[0])

                if team_stats == None:
                    print('Error → No such team')

                else:
                    for k, v in team_stats.items():
                        x.extend([round(el / 100, 2) for el in v])

                teams[row[0]] = team_stats
            
            if hasKey(teams, row[1]) == False:
                sys.stdout.write(f'Downloading team: {row[1]}... ')

                team_stats = stats(row[1])

                if team_stats == None:
                    print('Error → No such team')

                else:
                    for k, v in team_stats.items():
                        x.extend([round(el / 100, 2) for el in v])

                teams[row[1]] = team_stats

            if teams[row[0]] == None or teams[row[1]] == None:
                continue

            X.append(x)
            
            wdl = None # Win, Draw, Lose

            if row[2] == 'H':
                wdl = [1, 0, 0]
            elif row[2] == 'D':
                wdl = [0, 1, 0]
            else:
                wdl = [0, 0, 1]

            y.append(wdl)
        
        return (X, y)

X, y = loadData(datafile)
print()

with open(config['xDataFile'], 'w') as f:
    writer = csv.writer(f)
    
    writer.writerow([i + 1 for i in range(len(X[0]))])

    for x in X:
        writer.writerow(x)

with open(config['yDataFile'], 'w') as f:
    writer = csv.writer(f)

    writer.writerow(['Home', 'Draw', 'Away'])

    for el in y:
        writer.writerow(el)

print('Data saved to', config['xDataFile'], 'and', config['yDataFile'])