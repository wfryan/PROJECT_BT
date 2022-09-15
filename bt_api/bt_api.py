import os
import json
import hashlib
import time

from base64 import b64encode
from base64 import b64decode

from cryptography.fernet import Fernet
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from datetime import date, datetime

from flask import Flask
from flask_restful import Resource, Api, reqparse

GLOB_KEY = Fernet.generate_key()
fernet = Fernet(GLOB_KEY)

class bt_database():
    users_file_path = f"{os.getcwd()}/bt_database/bt_user_database.json"
    transactions_file_path = f"{os.getcwd()}/bt_database/bt_transaction_database.json"
    if not os.path.exists(users_file_path):
            open(users_file_path, 'w')
    if not os.path.exists(transactions_file_path):
            open(transactions_file_path, 'w')
    # Getters #
    @classmethod
    def get_user_data(cls, user_id):
        try:
            return json.load(open(cls.users_file_path, 'r'))[user_id]
        except:
            return None

    @classmethod
    def get_users_transactions(cls, user_id, transaction_id=None, from_date=None, to_date=None):
        try:
            users_transactions = json.load(open(cls.transactions_file_path, 'r'))[user_id]
        except:
            return None

        if transaction_id:
            return users_transactions[f"{transaction_id}"]

        from_date = date.min if not from_date else from_date
        to_date = date.max if not to_date else to_date

        filtered_users_transactions = []
        for transaction in users_transactions.values():
            transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d").date()
            if transaction_date > from_date and transaction_date < to_date:
                filtered_users_transactions.append(transaction)

        return filtered_users_transactions

    # Writers #
    @classmethod
    def add_user(cls, user_id, user_data):
        with open(cls.users_file_path, 'r+') as users_file:
            try:
                users_dict = json.load(users_file)
            except:
                users_dict = {}
            users_dict[user_id] = user_data
            users_file.seek(0)
            json.dump(users_dict, users_file, indent = 4)

    @classmethod
    def add_transactions(cls, user_id, new_transactions):
        with open(cls.transactions_file_path, 'r+') as transactions_file:
            try:
                transactions_dict = json.load(transactions_file)
            except:
                transactions_dict = {}
            if not transactions_dict.get(user_id):
                transactions_dict[user_id] = {}
            for transaction in new_transactions:
                transactions_dict[user_id][transaction] = new_transactions[transaction]
            transactions_file.seek(0)
            json.dump(transactions_dict, transactions_file, indent = 4)

class bt_auth():
    @classmethod
    def do_hash(cls, password, salt=None):
        if not salt:
            salt = get_random_bytes(16)
        byte_password = password.encode('utf-8')
        key = PBKDF2(byte_password, salt, 64, count=1000000, hmac_hash_module=SHA512)
        return key, salt

    @classmethod
    def encrypt_glob(cls, glob_dict):
        glob_string = json.dumps(glob_dict)
        enc_glob = fernet.encrypt(glob_string.encode())
        enc_glob_string = enc_glob.decode()
        return enc_glob_string

    @classmethod
    def decrypt_glob(cls, enc_glob_string):
        glob_string = fernet.decrypt(enc_glob_string).decode()
        glob_dict = json.loads(glob_string)
        return glob_dict

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
            return None
        glob_dict = cls.decrypt_glob(enc_glob_string)

        now = time.time()
        valid_until_time = glob_dict['valid_until']

        is_dead = valid_until_time <= now
        is_decaying = (valid_until_time - now) < 1800

        if is_dead:
            return None
        if is_decaying:
            glob_dict = cls.get_auth_glob(glob_dict['email'])

        return cls.encrypt_glob(glob_dict)

    @classmethod
    def get_user_id(cls, email=None, glob=None):
        if email:
            return hashlib.sha256(email.encode("utf-8")).hexdigest()[:32]
        elif glob:
            return cls.decrypt_glob(glob)['user_id']
        else:
            return None

class user(Resource):

    def get(self): # Login User
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        # Get user ID
        user_id = bt_auth.get_user_id(args['email'])

        # Check if user exists, and get data if they do
        if not (user_data := bt_database.get_user_data(user_id)):
            return {'message':f"Email and password do not match"}, 401

        saved_hash = b64decode(user_data['key'].encode('utf-8'))
        salt = b64decode(user_data['salt'].encode('utf-8'))
        check_hash = bt_auth.do_hash(args['password'], salt)[0]

        if saved_hash == check_hash:
            auth_glob = bt_auth.get_auth_glob(user_id)
            return {"auth_glob": auth_glob}, 200
        else:
            return {'message':f"Email and password do not match"}, 401

    def post(self): # Create New User
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        # Get user id
        user_id = bt_auth.get_user_id(args['email'])

        # Make sure user does not yet exist
        if bt_database.get_user_data(user_id):
            return {'message':"User already exists"}, 409

        # Get new user auth data
        key, salt = bt_auth.do_hash(args['password'])

        # Init new user sub dict
        new_user_data = {
            "email": args['email'],
            "key": b64encode(key).decode('utf-8'),
            "salt": b64encode(salt).decode('utf-8')
        }

        # Add new user to main users file, and init them in the transactions file
        bt_database.add_user(user_id, new_user_data)

        return 201


class transactions(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('auth_glob', required=True)
        parser.add_argument('transaction_id', required=False)
        # Dates are strings in YYYY-MM-DD ("%Y-%m-%d") format
        parser.add_argument('start', required=False)
        parser.add_argument('end', required=False)
        args = parser.parse_args()

        if auth_glob := bt_auth.check_auth_glob(args['auth_glob']):
            user_id = bt_auth.get_user_id(glob=auth_glob)
        else:
            return {'message':"Auth Glob is unauthorized"}, 401

        # Get transaction by id
        if transaction_id := args['transaction_id']:
            if transaction := bt_database.get_users_transactions(user_id, transaction_id=transaction_id):
                user_transactions = [transaction]
            else:
                return {'message':f"Transaction with {transaction_id} does not exist"}, 404
        # Get transactions in range
        else:
            from_datestring = args.get('start')
            to_datestring = args.get('end')

            from_date = datetime.strptime(from_datestring, "%Y-%m-%d").date() if from_datestring else None
            to_date = datetime.strptime(to_datestring, "%Y-%m-%d").date() if to_datestring else None
            user_transactions = bt_database.get_users_transactions(user_id, from_date=from_date, to_date=to_date)

        return {'transactions': user_transactions, 'auth_glob': auth_glob}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('auth_glob', required=True)
        parser.add_argument('transactions', required=True)
        args = parser.parse_args()

        if auth_glob := bt_auth.check_auth_glob(args['auth_glob']):
            user_id = bt_auth.get_user_id(glob=auth_glob)
        else:
            return {'message':"Auth Glob is unauthorized"}, 401

        transactions_to_create = json.loads(args['transactions'])['transactions']
        new_transactions = {}
        for new_transaction in transactions_to_create:
            # Input Data Checks
            if not new_transaction['date'] or not new_transaction['amount']:
                return { 'message':"Transactions require date and amount fields minimum"}, 400
            try:
                datetime.strptime(new_transaction['date'], "%Y-%m-%d")
            except:
                return { 'message':"Date must be formatted YYYY-MM-DD"}, 400

            # Create transaction id
            prehash_id = f"{new_transaction['date']}{new_transaction['amount']}"
            transaction_id = int((hashlib.sha1(prehash_id.encode('utf-8'))).hexdigest(), 16) % (10**10)
            if bt_database.get_users_transactions(user_id, transaction_id=transaction_id):
                continue
                return { 'message':"A collision occurred, please try again, if this happens more than once, there is a duplicate transaction"}, 500

            # Add transaction id to transaction and add transaction to new_transactions
            new_transaction['transaction_id'] = transaction_id
            new_transactions[transaction_id] = new_transaction

        if len(new_transactions) == 0:
            return {'message':"No transactions to create"}, 400
        bt_database.add_transactions(user_id, new_transactions)

        return {'created_transactions': new_transactions, 'auth_glob': auth_glob}, 201

app = Flask(__name__)
api = Api(app)

api.add_resource(transactions, '/transactions')
api.add_resource(user, '/user')

if __name__ == '__main__':
    app.run()