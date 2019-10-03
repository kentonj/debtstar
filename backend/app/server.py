from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS, cross_origin
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
app.config['CORS_HEADERS'] = 'Content-Type'
# @app.after_request
# def after_request(response):
#   response.headers.add('Access-Control-Allow-Origin', '*')
#   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#   return response

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

@app.route('/api/v1/store_access_token', methods=['POST'])
@cross_origin()
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
        data = {'error':'Appropriate values were not provided for user_id or public_token'}
        response = jsonify(data)
        response.status_code = 403
        return response

    try:
        exchange_response = plaid_client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        response = jsonify(format_error(e))
        response.status_code = 403
        return response
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

    data = {'item_id':item_id}
    # response.status = 200
    response = jsonify(data)
    response.status_code = 200

    return response

def extract_liability_summary(access_token):
    liabilities_response = plaid_client.Liabilities.get(access_token=access_token)
    account_details_list = []
    for account in liabilities_response.get('accounts'):
        # reset the balance to just be current balance
        account_dict = {}
        account_id = account.get('account_id')
        account_dict['account_id'] = account_id
        account_dict['current_balance'] = account['balances'].get('current')
        account_dict['name'] = account.get('name')
        account_dict['type'] = account.get('type')
        account_dict['subtype'] = account.get('subtype')
        
        if account.get('type') in ('credit', 'loan'):
            account_dict['is_debt'] = True
            liabilities_dict = liabilities_response.get('liabilities')
            
            # create list of accounts that match the id
            matching_student_dict_list = [x for x in liabilities_dict.get('student') if x['account_id'] == account_id]
            matching_credit_dict_list = [x for x in liabilities_dict.get('credit') if x['account_id'] == account_id]
            if len(matching_student_dict_list) == 1:
                liability_details = matching_student_dict_list[0]
                print(liability_details)
                account_dict['interest'] = liability_details['interest_rate_percentage']
                account_dict['minimum_payment'] =  liability_details['minimum_payment_amount']
            elif len(matching_student_dict_list) == 1:
                #this is the right loan details
                liability_details = matching_credit_dict_list[0]
                print(liability_details)
                account_dict['interest'] = [x for x in liability_details['aprs'] if x['type'] == 'purchase_apr'][0]
                account_dict['minimum_payment'] =  liability_details['minimum_payment_amount']
        else:
            account_dict['is_debt'] = False

        account_details_list.append(account_dict) 
    return account_details_list

@app.route('/api/v1/users/user_id/get_accounts_summary', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
@cross_origin()
def get_user_accounts_summary(user_id):
    # now get all my tokens or all my items
    all_accounts_list = []
    for token in Token.query.filter_by(user_id=user_id).all():
        # token.item_id and token.access_token
        access_token = token.access_token
        account_detail_list = extract_liability_summary(access_token)
        all_accounts_list += account_detail_list
    response = jsonify(all_accounts_list)
    # response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200
    return response

@app.route('api/v1/users/<id>/ping', methods=['GET', 'OPTIONS'])
@cross_origin()
def ping(id):
    data = {'pong':id}
    response = jsonify(data)
    resopnse.status_code = 200
    return response

@app.route('/getaccounts')
def get_accounts():
    token_id = ''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
