import json

from bt_api import bt_database
from bt_api import bt_auth

import bt_exception

import flask
from flask import Flask
from flask import request
from flask_restful import Resource, Api, reqparse

class user(Resource):

    def get(self): # Get auth_glob for existing user
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        try:
            auth_glob = bt_auth.user_login(email=args['email'], password=args['password'])
            return flask.Response(status=200, headers={'auth_glob': auth_glob})
        except bt_exception.bt_auth_error as error:
            return flask.Response(response={'message':error}, status=401)
        except:
            return flask.Response(status=500)

    def post(self): # Init new user
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('phone_num', required=False)
        args = parser.parse_args()

        try:
            bt_auth.create_user(args['email'], args['password'], args.get('phone_num'))
            return flask.Response(status=201)
        except bt_exception.bt_input_error as error:
            return flask.Response(response={'message':error}, status=400)
        except bt_exception.bt_conflict_error as error:
            return flask.Response(response={'message':error}, status=409)


class transactions(Resource):
    def get(self): # Get transactions
        parser = reqparse.RequestParser()
        parser.add_argument('transaction_id', required=False)
        # Dates are strings in YYYY-MM-DD ("%Y-%m-%d") format
        parser.add_argument('start_date', required=False)
        parser.add_argument('end_date', required=False)
        args = parser.parse_args()

        try:
            user_id, auth_glob = bt_auth.check_auth_glob(request.headers['auth_glob'])
            if transaction_id := args.get('transaction_id'):
                returned_transactions = bt_database.get_single_transaction(user_id, transaction_id)
            else:
                start_date = args.get('start_date')
                end_date = args.get('end_date')
                returned_transactions = bt_database.get_filtered_transactions(user_id, start_date=start_date, end_date=end_date)
            transactions_dict = {
                "transactions": returned_transactions
            }
            return flask.Response(response=json.dumps(transactions_dict), status=200, headers={'auth_glob': auth_glob})

        except bt_exception.bt_input_error as error:
            return flask.Response(response=error, status=400)
        except KeyError:
            return flask.Response(response="auth_glob is a required header", status=401)
        except bt_exception.bt_auth_error as error:
            return flask.Response(response=error, status=401)

    def post(self): # Create transactions
        parser = reqparse.RequestParser()
        parser.add_argument('transactions', required=True)
        args = parser.parse_args()

        try:
            user_id, auth_glob = bt_auth.check_auth_glob(request.headers['auth_glob'])
            transactions_list = json.loads(args['transactions'])
            num_new_transactions, num_duplicate_transactions = bt_database.create_transactions(user_id, transactions_list)
            status = 201 if num_new_transactions != 0 else 200
            response = {
                "Created Transactions": num_new_transactions,
                "Duplicate Transactions": num_duplicate_transactions
            }
            return flask.Response(response=json.dumps(response), status=status, headers={'auth_glob': auth_glob})

        except bt_exception.bt_input_error as error:
            return flask.Response(response={f"{error}"}, status=400)
        except KeyError as error:
            return flask.Response(response="auth_glob is a required header", status=401)
        except bt_exception.bt_auth_error as error:
            return flask.Response(response=error, status=401)


app = Flask(__name__)
api = Api(app)

api.add_resource(transactions, '/transactions')
api.add_resource(user, '/user')

if __name__ == '__main__':
    app.run(host='192.168.4.4', port=5000)