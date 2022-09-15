from wsgiref import headers
import requests
import json
import os
import time
import argparse
import csv

from bt_auth import bt_auth
from bt_database import bt_database

from datetime import datetime

class ingestDataError(Exception):
    pass
class btApiTestError(Exception):
    pass

bt_api_base_url = f"http://127.0.0.1:5000"

def create_user(email, password=None, phone_num=None):
    url = f"{bt_api_base_url}/user"
    data = {}
    data['email'] = email
    if password:
        data['password'] = password
    if phone_num:
        data['phone_num'] = phone_num
    response = requests.post(url, json=data)
    if response.status_code == 201:
        return
    else:
        raise btApiTestError(f"ERROR: Could not create user: {response.text}")

def login(email, password=None, phone_num=None):
    url = f"{bt_api_base_url}/user"
    data = {}
    data['email'] = email
    if password:
        data['password'] = password
    if phone_num:
        data['phone_num'] = phone_num
    response = requests.get(url, json=data)
    if response.status_code == 200:
        return response.headers['auth_glob']
    else:
        raise btApiTestError(f"ERROR: Cannot login: {response.text}")

def create_transactions(auth_glob, transactions_list):
    url = f"{bt_api_base_url}/transactions"
    data = {
        "transactions": json.dumps(transactions_list)
    }
    headers = {
        "auth_glob": auth_glob,
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201 or response.status_code == 200:
        return response.json()['Created Transactions'], response.headers['auth_glob']
    else:
        raise btApiTestError(f"ERROR: Could not create transactions: {response.text}")

def get_transactions(auth_glob, start_date=None, end_date=None):
    url = f"{bt_api_base_url}/transactions"
    data = {
        "start_date": start_date,
        "end_date": end_date
    }
    headers = {
        "auth_glob": auth_glob,
    }
    response = requests.get(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json(), response.headers['auth_glob']
    else:
        raise btApiTestError(f"ERROR: Could not get transactions: {response.text}")

def get_card_map(file_columns):
    card_data = {
        "Apple": {
            "file_headers": ['Transaction Date', 'Clearing Date', 'Description', 'Merchant', 'Category', 'Type', 'Amount (USD)', 'Purchased By'],
            "date_format": "%m/%d/%Y",
            "translation": {
                'Transaction Date': 'date',
                'Clearing Date': 'post_date',
                'Description': 'description',
                'Merchant': 'merchant',
                'Category': 'category',
                'Type': 'type',
                'Amount (USD)': 'amount',
                'Purchased By': None
            }
        },
        "Discover": {
            "file_headers": ['Trans. Date', 'Post Date', 'Description', 'Amount', 'Category'],
            "date_format": "%m/%d/%Y",
            "translation": {
                'Trans. Date': 'date',
                'Post Date': 'post_date',
                'Description': 'description',
                'Amount': 'amount',
                'Category': 'category'
            }
        }
    }
    for card_vendor in card_data.keys():
        if card_data[card_vendor]["file_headers"] == file_columns:
            return card_data[card_vendor]["date_format"], card_data[card_vendor]["translation"]

def get_files(transactionfolder):
    transaction_files = []
    for file in os.listdir(transactionfolder):
        if not file.endswith('.csv'):
            continue
        transaction_files.append(f"{transactionfolder}/{file}")
    return transaction_files

def add_transactions(transaction_file, transactions_list):
    file_data = csv.DictReader(open(transaction_file, 'r'))
    date_format, data_translator = get_card_map(file_data.fieldnames)
    for row in file_data:
        temp_transaction = {}
        for column in data_translator.keys():
            if new_column_name := data_translator[column]:
                column_data = row[column]
                if 'date' in new_column_name:
                    column_data = datetime.strftime(datetime.strptime(column_data, date_format), "%Y-%m-%d")

                temp_transaction[new_column_name] = column_data
        if float(temp_transaction['amount']) >= 0:
            transactions_list.append(temp_transaction)

def args_check(args):
    if not args.transactionfolder:
        raise ingestDataError("ERROR: --tr folder is required")
    args.transactionfolder = os.path.expandvars(os.path.expanduser(args.transactionfolder))
    if not os.path.isdir(args.transactionfolder):
        raise ingestDataError(f"ERROR: --tr folder does not exist: {args.cksumfolder}")

def args_get():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tr', '--transactionfolder', help=r'Folder that transaction data is stored in')

    args = parser.parse_args()
    return args

def login_or_create(email, password=None, phone_num=None):
    try:
        return login(email, password, phone_num)
    except:
        create_user(email=email, password=password, phone_num=phone_num)
        return login(email, password, phone_num)

def main():
    args = args_get()
    args_check(args)

    transaction_files = get_files(args.transactionfolder)

    transactions = []
    for file in transaction_files:
        add_transactions(file, transactions)

    # Web / App Test
    print("Ethan App:")
    ethan_glob = login_or_create(email="ethanrousseau99@gmail.com", password="pokeyup")

    start_time = time.time()
    num_created_transactions, ethan_glob = create_transactions(ethan_glob, transactions)
    print(f"Took {time.time() - start_time}s to write {num_created_transactions} transactions")

    #transactions, ethan_glob = get_transactions(ethan_glob, "2022-01-01", "2022-09-17")
    transactions, ethan_glob = get_transactions(ethan_glob)
    for transaction in transactions:
        print(f"{transaction['date']} - {transaction['amount']}")

    # SMS Test
    print("Jenna SMS:")
    jenna_phone = "7816402775"
    if not bt_database.does_user_exist(phone_num=jenna_phone):
        bt_auth.create_user("jenna@gmail.com", phone_num=jenna_phone)
    user_id = bt_database.get_user_id_from_phone_num(jenna_phone)

    transactions = []
    purchase = {
        "date": "2022-04-20",
        "amount": 69.69
    }
    transactions.append(purchase)
    bt_database.create_transactions(user_id, transactions)
    returned_transactions = bt_database.get_filtered_transactions(user_id)
    for transaction in returned_transactions:
        print(transaction)

if __name__ == "__main__":
    main()