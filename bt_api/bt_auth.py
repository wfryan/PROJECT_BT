import os
import json
import hashlib
import re
import time

from bt_database import bt_database
import bt_exception

from base64 import b64encode
from base64 import b64decode

from cryptography.fernet import Fernet
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

class bt_auth():

    GLOB_KEY = Fernet.generate_key()
    fernet = Fernet(GLOB_KEY)

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
        enc_glob = cls.fernet.encrypt(glob_string.encode())
        enc_glob_string = enc_glob.decode()
        return enc_glob_string

    @classmethod
    def decrypt_glob(cls, enc_glob_string):
        return json.loads(cls.fernet.decrypt(bytes(enc_glob_string, 'utf-8')).decode())

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
            glob_dict = cls.get_auth_glob(glob_dict['user_id'])

        user_id = glob_dict['user_id']
        return user_id, cls.encrypt_glob(glob_dict)

    @classmethod
    def get_user_id(cls, email=None, phone_num=None):
        if not email and not phone_num:
            raise bt_exception.bt_input_error("email or phone_num are required to get user id")
        if email:
            return hashlib.sha256(email.encode("utf-8")).hexdigest()[:32]
        if phone_num:
            return bt_database.get_user_id_from_phone_num(phone_num)

    @classmethod
    def create_user(cls, email, password=None, phone_num=None): # Init new user
        # Check if valid email
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(email_regex, email):
            raise bt_exception.bt_input_error("Email is not valid email address")

        if not password and not phone_num:
            raise bt_exception.bt_input_error("password or phone_num required to create account")

        # Get user id
        user_id = cls.get_user_id(email)

        # Make sure user does not yet exist
        if bt_database.does_user_exist(user_id):
            raise bt_exception.bt_conflict_error("User already exists")

        # Init new user sub dict
        new_user_data = {}
        new_user_data['email'] = email
        new_user_data['user_id'] = user_id

        if password: # Add password data if applicable
            key, salt = cls.do_hash(password)
            new_user_data['key'] = b64encode(key).decode('utf-8')
            new_user_data['salt'] = b64encode(salt).decode('utf-8')

        if phone_num: # Add phone number if applicable
            new_user_data['phone_num'] = phone_num
            bt_database.write_to_phone_map(user_id, phone_num=phone_num)

        # Add new user to main users file, and init them in the transactions file
        bt_database.write_to_user_file(user_id, new_user_data=new_user_data, new_transactions={}, new_date_map={})

    @classmethod
    def user_login(cls, email, password, user_id=None): # Return auth_glob to authenticate further requests if given password, returns user_id otherwards
        # Get user id
        user_id = bt_auth.get_user_id(email)
        # Check if user exists, throw exception if they don't
        if not bt_database.does_user_exist(user_id=user_id):
            raise bt_exception.bt_auth_error("User does not exist")

        # Get user id
        if not user_id:
            user_id = cls.get_user_id(email=email)

        # Get users data
        user_data = bt_database.get_user_data(user_id)

        # Check if given password matches hash at user_id, and return 1 hour validated glob if so
        if cls.check_user_hash(user_key=user_data['key'], user_salt=user_data['salt'], user_password=password):
            return cls.get_auth_glob(user_id)
        else:
            raise bt_exception.bt_auth_error("Incorrect email or password")
