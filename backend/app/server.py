from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
from flask_cors import CORS, cross_origin
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers, Origin, X-Requested-With, Content-Type, Accept, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    response.headers.add('Access-Control-Expose-Headers', '*')

import psycopg2
import os
import plaid
from dbmodels import Token

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# Project ID is determined by the GCLOUD_PROJECT environment variable
# db = firestore.Client(project='debt-star')
firebase_cred = credentials.Certificate('../debt-star-firebase-adminsdk-key.json')
firebase_app = initialize_app(firebase_cred)
firestore_db = firestore.client()

app = Flask(__name__)
db_uri = 'postgresql://{user}:{pw}@{host}:{port}/{db}'\
            .format(user=POSTGRES_USER, pw=POSTGRES_PASSWORD,
                    host=POSTGRES_HOST, port=POSTGRES_PORT, db=POSTGRES_DB)
print('using db uri:', db_uri)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
db = SQLAlchemy(app)

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.environ.get('PLAID_PUBLIC_KEY')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.environ.get('PLAID_PRODUCTS')
PLAID_COUNTRY_CODES = os.environ.get('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')

plaid_client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, 
                      api_version='2019-05-29')

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

@app.route('/api/v1/store_access_token', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def store_access_token():
    '''
    expected_payload = {
        'uuid':'thispersonsuuidjkdlf;ajkfld;sa',
        'public_token':'this is a public token'
    }
    '''
    result = request.get_json()
    user_id = result.get('user_id')
    public_token = result.get('public_token')

    if user_id is None or public_token is None:
        response = {'status':500, 'error':'Appropriate values were not provided for user_id or public_token'}
        return jsonify(response)

    try:
        exchange_response = plaid_client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))
    access_token = exchange_response.get('access_token')
    item_id = exchange_response.get('item_id')
    
    # store token in local database
    token = Token(user_id=user_id, item_id=item_id, public_token=public_token, access_token=access_token)
    token.upsert()

    # now it is stored in firestore
    fb_item = firestore_db.collection('items').document(item_id)
    fb_item.set({
        'user_id': user_id,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    response = {'status':'200', 'item_id':item_id}

    # now, use the token to retrieve stuff about the item

    return jsonify(response)

def get_account_details(account_id, account_list):
    for account in account_list:
        if account_id == account['account_id']:
            return account

def summarize_student_debt(student_debt, all_accounts):
    student_debt_list = []
    for debt in student_debt:
        debt_dict = {}
        account_details = get_account_details(debt['account_id'], all_accounts)
        # loan name, total, interest, monthly payment, period
        debt_dict['account_id'] = debt['account_id']
        debt_dict['name'] = account_details.get('name')
        debt_dict['loan_name'] = debt['loan_name']
        debt_dict['interest_rate'] = debt['interest_rate_percentage']
        debt_dict['balance'] = debt['last_statement_balance']
        debt_dict['expected_payoff_date'] = debt['expected_payoff_date']
        debt_dict['last_payment_amount'] = debt['last_payment_amount']
        debt_dict['minimum_payment_amount'] = debt['minimum_payment_amount']
        # debt_dict['payments_remaining'] = debt['pslf_status']['payments_remaining']
        student_debt_list.append(debt_dict)
    return student_debt_list

def normalize_interest_rate(interest_list):
    # TODO: fix this, just calculates average right now
    apr_list = [x['apr_percentage'] for x in interest_list]
    avg_apr = sum(apr_list)/len(apr_list)
    return round(avg_apr,4)

def summarize_credit_debt(credit_debt, all_accounts):
    credit_debt_list = []
    for debt in credit_debt:
        debt_dict = {}
        account_details = get_account_details(debt['account_id'], all_accounts)
        # loan name, total, interest, monthly payment, period
        debt_dict['account_id'] = debt['account_id']
        debt_dict['name'] = account_details.get('name')
        debt_dict['purchase_apr'] = [x['apr_percentage'] for x in debt['aprs'] if x['apr_type'] == 'purchase_apr'][0]
        # calculate effective interest rate across loans
        debt_dict['normalized_apr'] = normalize_interest_rate(debt['aprs'])
        debt_dict['balance'] = debt['last_statement_balance']
        debt_dict['last_payment_amount'] = debt['last_payment_amount']
        debt_dict['minimum_payment_amount'] = debt['minimum_payment_amount']
        # debt_dict['payments_remaining'] = debt['pslf_status']['payments_remaining']
        credit_debt_list.append(debt_dict)
    return credit_debt_list

@app.route('/api/v1/summarize_liabilities', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def summarize_liabilities():
    ''' TODO: take in user_id
    get all accounts tied to the user, iterate through each account, 
        assemble a big list of all student debts
        assemble a big list of all credit debts
    return to front end
    '''
    result = request.get_json()
    user_id = result.get('user_id')
    # now get all my tokens or all my items
    all_student_debt_list = []
    all_credit_debt_list = []
    for token in Token.query.filter_by(user_id=user_id).all():
        # token.item_id and token.access_token
        access_token = token.access_token
        account_response = plaid_client.Accounts.get(access_token)
        liabilities_response = plaid_client.Liabilities.get(access_token)
        all_accounts = account_response.get('accounts')
        student_debt = liabilities_response['liabilities'].get('student')
        credit_debt = liabilities_response['liabilities'].get('credit')
        print('credit debt:', credit_debt)
        student_debt_list = summarize_student_debt(student_debt, all_accounts)
        credit_debt_list = summarize_credit_debt(credit_debt, all_accounts)
        if student_debt_list is not None:
            all_student_debt_list += student_debt_list
        if credit_debt_list is not None:
            all_credit_debt_list += credit_debt_list

    # TODO: make sure i only have unique account ids in each list
    return {'student':all_student_debt_list, 'credit':all_credit_debt_list}


@app.route('/')
def ping():
    return 'pong'

@app.route('/getaccounts')
def get_accounts():
    token_id = ''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
