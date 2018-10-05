from bs4 import BeautifulSoup
import json

data = ''
with open("rozklad.html") as file:
    data += file.read()
soup = BeautifulSoup(data, "lxml")

distribution = {}
colors = ['S', 'H', 'D', 'C']
players = ['N', 'E', 'S', 'W']
for i, td in enumerate(soup.findAll('td', attrs={'class': 'w'})):
    hand = []
    for j, color in enumerate(colors):
        row = td.contents[2+4*j].strip().split(" ")
        suit = [r + colors[j] for r in row]
        hand += suit
    distribution[players[i]] = hand

with open("json/distribution.json", "w") as f:
    json.dump(distribution, f)