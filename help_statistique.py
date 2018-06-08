
import requests
t=requests.get('http://localhost:3333/calcul_statistique')
print(t.status_code)