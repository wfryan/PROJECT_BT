import requests
import json
import os
import time

url = "http://127.0.0.1:5000/user"
data = {'email': "ethanrousseau99@gmail.com", "password": "pokeyup"}
response = requests.post(url, json=data)
print(response.json())

url = "http://127.0.0.1:5000/user"
data = {'email': "jennac5903@gmail.com", "password": "jennac"}
response = requests.post(url, json=data)
print(response.json())

url = "http://127.0.0.1:5000/user"
data = {'email': "ethanrousseau99@gmail.com", "password": "pokeyup"}
response = requests.get(url, json=data)
print(response.json())
if response.status_code == 200:
    ethan_glob = response.json()['auth_glob']

url = "http://127.0.0.1:5000/transactions"
transactions = {
    "transactions": [
        {
            "date": "2022-09-13",
            "amount": 500,
            "merchant": "apple"
        },
        {
            "date": "2022-09-13",
            "amount": 500,
            "merchant": "apple"
        }
    ]
}
data = {
    "auth_glob": ethan_glob,
    "transactions": json.dumps(transactions)
}
response = requests.post(url, json=data)
print(response)
if response.status_code == 201:
    ethan_glob = response.json()['auth_glob']

url = "http://127.0.0.1:5000/transactions"
data = {"auth_glob": ethan_glob}
response = requests.get(url, json=data)
print(response.json())
if response.status_code == 200:
    ethan_glob = response.json()['auth_glob']

pass