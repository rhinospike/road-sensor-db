import requests
import random
import datetime

#url = 'https://road-sensor-db.herokuapp.com'
url = "http://localhost:5000"

newsensor = {"sensorid": '5',"latitude":random.random(),"longitude":random.random()}
requests.post(url + '/sensors',json=newsensor)

r = requests.get(url + '/sensors')
print(r.json())

print("Initial:")
r = requests.get(url + '/readings?')
print(r.json())
print()

newreading = {"sensorid" : '5', "messageid":1, "hops":0, "timestamp" : str(datetime.datetime.now()), "sensors":{"dust" : random.random() }}
requests.post(url + '/readings', json=[newreading])

print("Final:")
r = requests.get(url + '/readings?')
print(r.json())
print()
