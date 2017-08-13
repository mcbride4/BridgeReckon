from bs4 import BeautifulSoup
import json

data = ''
with open("rozklad.html") as file:
    data += file.read()

'''<div class="image">
        <a href="http://www.example.com/eg1">Content1<img  
        src="http://image.example.com/img1.jpg" /></a>
        </div>
        <div class="image">
        <a href="http://www.example.com/eg2">Content2<img  
        src="http://image.example.com/img2.jpg" /> </a>
        </div>'''

soup = BeautifulSoup(data, "lxml")

distribution = {}
colors = ['S', 'H', 'D', 'C']
players = ['N', 'E', 'S', 'W']
for i, td in enumerate(soup.findAll('td', attrs={'class':'w'})):
    #print(td)
    #for i in range(15):
        # print(str(i) + str(td.contents[i]))
    hand = []
    for j, color in enumerate(colors):
        row = td.contents[2+4*j].strip().split(" ")
        suit = [r + colors[j] for r in row]
        hand += suit
    #print(hand)
    distribution[players[i]] = hand
    #spades_row = td.contents[2].strip().split(" ")
    #spades = [s + 'S' for s in spades_row]


    #print(spades)
    #print(td.contents[6])
    #print(td.contents[10])
    #print(td.contents[14])

print(distribution)

with open("distribution.json", "w") as f:
    json.dump(distribution, f)