import os
import json
import hashlib

import bt_exception

from datetime import date, datetime


class bt_database():
    bt_database_path = os.getenv('BT_DATABASE_PATH')
    if bt_database_path.endswith('/'):
        bt_database_path = bt_database_path[:-1]
    users_dir_path = f"{bt_database_path}/users"
    phone_map_path = f"{bt_database_path}/phone_map.json"
    if not os.path.exists(bt_database_path):
        os.makedirs(bt_database_path)
    if not os.path.exists(users_dir_path):
        os.makedirs(users_dir_path)
    if not os.path.exists(phone_map_path):
        json.dump({}, open(phone_map_path, 'w'))

    # Getters #
    @classmethod
    def does_user_exist(cls, user_id=None, phone_num=None): # Returns bool
        if not user_id and not phone_num:
            raise bt_exception.bt_input_error("user_id or phone_num are required to check if user exists")
        return (os.path.exists(f"{cls.users_dir_path}/{user_id}.json") or json.load(open(cls.phone_map_path, 'r')).get(phone_num))

    @classmethod
    def get_user_id_from_phone_num(cls, phone_num):
        return json.load(open(cls.phone_map_path, 'r'))[phone_num]

    @classmethod
    def get_user_data(cls, user_id):
        return json.load(open(f"{cls.users_dir_path}/{user_id}.json", 'r'))['user_data']

    @classmethod
    def get_users_transactions(cls, user_id):
        return json.load(open(f"{cls.users_dir_path}/{user_id}.json", 'r'))['user_transactions']

    @classmethod
    def get_date_map(cls, user_id):
        return json.load(open(f"{cls.users_dir_path}/{user_id}.json", 'r'))['date_map']

    @classmethod
    def get_single_transaction(cls, user_id, transaction_id): # Get a single transaction by transaction_id
        try:
            return bt_database.get_users_transactions(user_id)['transaction_id']
        except KeyError:
            raise bt_exception.bt_input_error(f"Transaction with id {transaction_id} does not exist")

    @classmethod
    def get_filtered_transactions(cls, user_id, start_date=None, end_date=None): # Get transactions with optional filters
        # Get all users transactions from file
        users_transactions = bt_database.get_users_transactions(user_id)

        from_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.min
        to_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.max

        filtered_transactions = []
        for transaction in users_transactions.values():
            transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d").date()
            if transaction_date > from_date and transaction_date < to_date:
                filtered_transactions.append(transaction)

        return filtered_transactions

    # Setters #
    @classmethod
    def write_to_phone_map(cls, user_id, phone_num):
        phone_dict = json.load(open(cls.phone_map_path, 'r'))
        phone_dict[phone_num] = user_id
        json.dump(phone_dict, open(cls.phone_map_path, 'w'))

    @classmethod
    def write_to_user_file(cls, user_id, new_user_data=None, new_transactions=None, new_date_map=None):
        user_file_path = f"{cls.users_dir_path}/{user_id}.json"
        if not os.path.exists(user_file_path):
            json.dump({}, open(user_file_path, 'w'))
            user_dict = {}
        else:
            user_dict = json.load(open(user_file_path, 'r'))

        if new_user_data != None:
            if not (existing_user_data := user_dict.get('user_data')):
                existing_user_data = {}
            user_dict['user_data'] = existing_user_data | new_user_data

        if new_transactions != None:
            if not (existing_transactions := user_dict.get('user_transactions')):
                existing_transactions = {}
            user_dict['user_transactions'] = existing_transactions | new_transactions

        if new_date_map != None:
            if not (existing_date_map := user_dict.get('date_map')):
                existing_date_map = {}
            user_dict['date_map'] = existing_date_map | new_date_map

        json.dump(user_dict, open(user_file_path, 'w'), indent = 4)

    @classmethod
    def create_transactions(cls, user_id, transactions): # Create transactions
        users_transactions = bt_database.get_users_transactions(user_id)
        new_transactions = {}
        num_duplicate_transactions = 0
        for input_transaction in transactions:
            new_transaction = {}
            # Input Data Checks
            if transaction_date := input_transaction.get('date'):
                try:
                    datetime.strptime(transaction_date, "%Y-%m-%d")
                    new_transaction['date'] = transaction_date
                except:
                    raise bt_exception.bt_input_error("Date must be formatted YYYY-MM-DD")
            else:
                raise bt_exception.bt_input_error("'date' field is required")

            try:
                if (transaction_amount := float(input_transaction['amount'])) >= 0:
                    new_transaction['amount'] = transaction_amount
                else:
                    raise bt_exception.bt_input_error()
            except:
                raise bt_exception.bt_input_error("A positive float 'amount' field is required")

            if transaction_merchant := input_transaction.get('merchant'):
                new_transaction['merchant'] = transaction_merchant

            if transaction_description := input_transaction.get('description'):
                new_transaction['description'] = transaction_description

            # Create transaction id
            prehash_id = ''
            for value in new_transaction.values():
                prehash_id = prehash_id + str(value)
            transaction_id = int((hashlib.sha1(prehash_id.encode('utf-8'))).hexdigest(), 16) % (10**10)
            if users_transactions.get(str(transaction_id)):
                num_duplicate_transactions += 1
                continue

            # Add transaction id to transaction and add transaction to new_transactions
            new_transaction['transaction_id'] = transaction_id
            new_transactions[transaction_id] = new_transaction

        if not (num_new_transactions := len(new_transactions)) == 0:
            bt_database.write_to_user_file(user_id, new_transactions=new_transactions)

        return num_new_transactions, num_duplicate_transactions

    @classmethod
    def build_date_map(cls, user_id, transactions):
        date_dict = cls.get_date_map(user_id)
        for transaction_id in transactions:
            if not (transactions_at_date_list := date_dict.get(cls.get_single_transaction(transaction_id)['date'])):
                transactions_at_date_list = []
            transactions_at_date_list.append(transaction_id)