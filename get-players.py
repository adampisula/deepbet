from lxml import html
import requests
import sys

base_url = 'https://sofifa.com'

def stats(team_url):
    print('URL: ', team_url)

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

# Search page
if len(sys.argv) > 1:
    search_url = base_url + '/teams?keyword=' + sys.argv[1]

else:
    search_url = base_url + '/teams?keyword=' + input("Team: ")

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

selected = (elements[selectedIndex], elements[selectedIndex+ 1])
print(f'Selected \'{selected[0]} ← {selected[1]}\'.')

expression = '//div[contains(@class, \'col-name\') and contains(@class, \'text-ellipsis\') and contains(@class, \'rtl\')]/a/@href'
team_url = base_url + tree.xpath(expression)[selectedIndex]

# Team's stats
team_stats = stats(team_url)

[print('\t', key, '→', val) for key, val in team_stats.items()]