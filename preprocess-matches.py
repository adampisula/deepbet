# Use this to export data in a more Python-friendly manner
# e.g. https://datahub.io/sports-data/spanish-la-liga

import csv

filename = 'data/season-1819.csv'
maxamount = 10
savefile = 'data/season-1819.min.csv'
data = ['HomeTeam', 'AwayTeam', 'FTR']
newDataNames = ['Home', 'Away', 'Result']
dataIndices = []
matches = [newDataNames]

print('Reading...')

with open(filename, 'r') as f:
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

print('Writing...')

with open(savefile, 'w') as f:
    writer = csv.writer(f)

    for match in matches:
        writer.writerow(match)

print(f'Processed {len(matches) - 1} matches.')