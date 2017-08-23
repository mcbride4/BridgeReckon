import requests

r = requests.get('http://www.pzbs.pl/wyniki/liga/liga2016-17/1liga/s/srr6b-13.html')
print(r.status_code)
with open("rozklad.html", "w") as file:
	file.write(r.text)
