import os
import json
import hashlib
import re
import time

import bt_exception

from base64 import b64encode
from base64 import b64decode

from cryptography.fernet import Fernet
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from datetime import date, datetime

from pathlib import Path

GLOB_KEY = Fernet.generate_key()
fernet = Fernet(GLOB_KEY)

class bt_database():
    bt_database_path = os.getenv('BT_DATABASE_PATH')
    users_file_path = f"{bt_database_path}/bt_user_database.json"
    transactions_file_path = f"{bt_database_path}/bt_transaction_database.json"
    if not os.path.exists(bt_database_path):
        os.makedirs(bt_database_path)

    try:
        json.load(open(users_file_path, 'r'))
    except:
        open(users_file_path, 'w').write("{}")
    try:
        json.load(open(transactions_file_path, 'r'))
    except:
        open(transactions_file_path, 'w').write("{}")

    @classmethod
    def does_user_exist(cls, user_id):
        if json.load(open(cls.users_file_path, 'r')).get(user_id):
            return True
        return False

    @classmethod
    def get_user_data(cls, user_id):
        return json.load(open(cls.users_file_path, 'r'))[user_id]

    @classmethod
    def get_users_transactions(cls, user_id):
        return json.load(open(cls.transactions_file_path, 'r'))[user_id]

    @classmethod
    def add_user(cls, user_data):
        with open(cls.users_file_path, 'r+') as users_file:
            try:
                users_dict = json.load(users_file)
            except:
                users_dict = {}
            user_id = user_data['user_id']
            users_dict[user_id] = user_data
            users_file.seek(0)
            json.dump(users_dict, users_file, indent = 4)
        cls.add_transactions(user_id, {})
        if phone_num := user_data.get('phone_num'):
            cls.change_user_phone(user_id, phone_num)

    @classmethod
    def change_user_phone(cls, user_id, phone_num):
        with open(cls.phone_map_path, 'r+') as phone_file:
            try:
                phones_dict = json.load(phone_file)
            except:
                phones_dict = {}
            phones_dict[phone_num] = user_id
            phone_file.seek(0)
            json.dump(phones_dict, phone_file, indent = 4)

    @classmethod
    def add_transactions(cls, user_id, new_transactions):
        with open(cls.transactions_file_path, 'r+') as transactions_file:
            try:
                transactions_dict = json.load(transactions_file)
            except:
                transactions_dict = {}
            if not transactions_dict.get(user_id):
                transactions_dict[user_id] = {}
            for transaction_id in new_transactions:
                transactions_dict[user_id][transaction_id] = new_transactions[transaction_id]
            transactions_file.seek(0)
            json.dump(transactions_dict, transactions_file, indent = 4)

    @classmethod
    def get_single_transaction(self, user_id, transaction_id): # Get a single transaction by transaction_id
        try:
            return bt_database.get_users_transactions(user_id)['transaction_id']
        except KeyError:
            raise bt_exception.bt_input_error(f"Transaction with id {transaction_id} does not exist")

    @classmethod
    def get_filtered_transactions(self, user_id, start_date=None, end_date=None): # Get transactions
        # Get all users transactions from file
        users_transactions = bt_database.get_users_transactions(user_id)

        from_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.min
        to_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.max

        filtered_transactions = {}
        for transaction in users_transactions.values():
            transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d").date()
            if transaction_date > from_date and transaction_date < to_date:
                filtered_transactions[transaction['transaction_id']] = transaction

        return filtered_transactions

    @classmethod
    def create_transactions(self, user_id, transactions): # Create transactions
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
            bt_database.add_transactions(user_id, new_transactions)

        return num_new_transactions, num_duplicate_transactions

class bt_auth():

    @classmethod
    def do_hash(cls, password, salt=None):
        if not salt:
            salt = get_random_bytes(16)
        byte_password = password.encode('utf-8')
        key = PBKDF2(byte_password, salt, 64, count=1000000, hmac_hash_module=SHA512)
        return key, salt

    @classmethod
    def check_user_hash(cls, user_key, user_salt, user_password):
        saved_hash = b64decode(user_key.encode('utf-8'))
        salt = b64decode(user_salt.encode('utf-8'))
        return True if saved_hash == cls.do_hash(user_password, salt)[0] else False

    @classmethod
    def encrypt_glob(cls, glob_dict):
        glob_string = json.dumps(glob_dict)
        enc_glob = fernet.encrypt(glob_string.encode())
        enc_glob_string = enc_glob.decode()
        return enc_glob_string

    @classmethod
    def decrypt_glob(cls, enc_glob_string):
        return json.loads(fernet.decrypt(bytes(enc_glob_string, 'utf-8')).decode())

    @classmethod
    def get_auth_glob(cls, user_id):
        now = time.time()
        glob_dict = {
            "created": now,
            "valid_until": now + 3600, # valid for 1 hour
            "user_id": user_id
        }
        return cls.encrypt_glob(glob_dict)

    @classmethod
    def check_auth_glob(cls, enc_glob_string):
        if type(enc_glob_string).__name__ != 'str':
            raise bt_exception.bt_input_error("auth_glob improper format")
        glob_dict = cls.decrypt_glob(enc_glob_string)

        now = time.time()
        valid_until_time = glob_dict['valid_until']

        is_dead = valid_until_time <= now
        is_decaying = (valid_until_time - now) < 1800

        if is_dead:
            raise bt_exception.bt_auth_error("auth_glob is expired")
        if is_decaying:
            glob_dict = cls.get_auth_glob(glob_dict['email'])

        user_id = glob_dict['user_id']
        return user_id, cls.encrypt_glob(glob_dict)

    @classmethod
    def get_user_id(cls, email=None):
        return hashlib.sha256(email.encode("utf-8")).hexdigest()[:32]

    @classmethod
    def create_user(self, email, password, phone_num=None): # Init new user
        # Check if valid email
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(email_regex, email):
            raise bt_exception.bt_input_error("Email is not valid email address")

        # Get user id
        user_id = bt_auth.get_user_id(email)

        # Make sure user does not yet exist
        if bt_database.does_user_exist(user_id):
            raise bt_exception.bt_conflict_error("User already exists")

        # Get new user auth data
        key, salt = bt_auth.do_hash(password)

        # Init new user sub dict
        new_user_data = {}
        new_user_data['user_id'] = user_id
        new_user_data['email'] = email
        if phone_num:
            new_user_data['phone_num'] = phone_num
        new_user_data['key'] = b64encode(key).decode('utf-8')
        new_user_data['salt'] = b64encode(salt).decode('utf-8')

        # Add new user to main users file, and init them in the transactions file
        bt_database.add_user(new_user_data)

    @classmethod
    def user_login(self, email, password): # Return auth_glob to authenticate further requests
        # Get user ID
        user_id = bt_auth.get_user_id(email)

        # Check if user exists, throw exception if they don't
        if not bt_database.does_user_exist(user_id):
            raise bt_exception.bt_auth_error("User does not exist")
        # Get users data
        user_data = bt_database.get_user_data(user_id)
        # Check if given password matches hash at user_id
        if bt_auth.check_user_hash(user_key=user_data['key'], user_salt=user_data['salt'], user_password=password):
            return bt_auth.get_auth_glob(user_id)
        else:
            raise bt_exception.bt_auth_error("Incorrect email or password")

