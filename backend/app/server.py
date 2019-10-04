from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from firebase_admin import credentials, firestore, initialize_app
import psycopg2
import os
import plaid
from dbmodels import Token, SuperCollection

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.environ.get('PLAID_PUBLIC_KEY')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.environ.get('PLAID_PRODUCTS')
PLAID_COUNTRY_CODES = os.environ.get('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

db_uri = 'postgresql://{user}:{pw}@{host}:{port}/{db}'\
            .format(user=POSTGRES_USER, pw=POSTGRES_PASSWORD,
                    host=POSTGRES_HOST, port=POSTGRES_PORT, db=POSTGRES_DB)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
db = SQLAlchemy(app)

firebase_cred = credentials.Certificate('../debt-star-firebase-adminsdk-key.json')
firebase_app = initialize_app(firebase_cred)
firestore_db = firestore.client()

plaid_client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, 
                      api_version='2019-05-29')

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

@app.route('/api/v1/store_access_token', methods=['POST'])
def store_access_token():
    '''
    expected_payload = {
        'user_id':'thispersonsuuidjkdlf;ajkfld;sa',
        'public_token':'this is a public token'
    }
    '''
    params = request.get_json()
    user_id = params.get('user_id')
    public_token = params.get('public_token')

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

    item_collection = SuperCollection(firestore_db.collection('items'), 'item_id')
    exchange_response.pop('access_token')
    exchange_response['user_id'] = user_id
    item_collection.write(exchange_response)

    # now also store all accounts from that item in firestore too
    accounts_response = plaid_client.Accounts.get(access_token=access_token)
    account_collection = SuperCollection(firestore_db.collection('accounts'), 'account_id')
    for account in accounts_response['accounts']:
        account['user_id'] = user_id
        account['item_id'] = item_id
        print('storing this account:', account)
        account_collection.write(account)
    
    liability_summary_list = extract_liability_summary(access_token)
    liability_collection = SuperCollection(firestore_db.collection('liabilities'))
    for liability in liability_summary_list:
        liability['user_id'] = user_id
        liability['item_id'] = item_id
        print('storing this liability:', liability)
        liability_collection.write(liability)

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
                account_dict['interest'] = liability_details['interest_rate_percentage'] / 100.0
                account_dict['minimum_payment'] =  liability_details['minimum_payment_amount']
            elif len(matching_credit_dict_list) == 1:
                #this is the right loan details
                liability_details = matching_credit_dict_list[0]
                account_dict['interest'] = [x['apr_percentage'] for x in liability_details['aprs'] if x['apr_type'] == 'purchase_apr'][0] / 100.0
                account_dict['minimum_payment'] =  liability_details['minimum_payment_amount']
        else:
            account_dict['is_debt'] = False
        account_details_list.append(account_dict)
    return account_details_list

@app.route('/api/v1/get_accounts_summary', methods=['GET'])
def get_accounts_summary():
    if request.method == 'GET':
        params = request.args
        user_id = params.get('user_id', None)
        if user_id is None:
            data = None
            response = jsonify(data)
            response.status_code = 403
        else:
            liabilities_collection = SuperCollection(firestore_db.collection('liabilities'))
            all_accounts_list = liabilities_collection.get_by_user(user_id)
            response = jsonify(all_accounts_list)
            response.status_code = 200
        return response

# sanity check route
@app.route('/get_test', methods=['GET'])
def get_test():
    if request.method == 'GET':
        user_id = request.args.get('user_id', 'no user_id found')
        data = {'user_id':user_id}
        response = jsonify(data)
        response.status_code = 200
    else:
        data = {'sampledata':None}
        response = jsonify(data)
        response.status_code = 403
    return response

# sanity check route
@app.route('/post_test', methods=['POST'])
def post_test():
    parameters = request.get_json()
    print('method: {}, parameters: {}'.format(request.method, parameters))
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data is None:
            return jsonify({'sampledata':None})
        user_id = post_data.get('user_id')
        data = {'user_id':user_id}
        response = jsonify(data)
        response.status_code = 200
    else:
        data = {'sampledata':None}
        response = jsonify(data)
        response.status_code = 403

    return response

def store_account_transactions(access_token, n_months, user_id):
    now = datetime.now()
    end = now.strftime('%Y-%m-%d')
    start = (now - timedelta(n_months*365/12)).strftime('%Y-%m-%d')
    transactions_response = plaid_client.Transactions.get(access_token=access_token, start_date=start, end_date=end)
    transactions_collection = SuperCollection(collection=firestore_db.collection('transactions'),
                                                pk_col='transaction_id')
    keys_list = []
    for transaction in transactions_response['transactions']:
        transaction_id = transactions_collection.write(transaction)
        keys_list.append(transaction_id)
    return keys_list

@app.route('/api/v1/sync_transactions', methods=['POST'])
def sync_transactions():
    '''
    params:
    user_id
    n_months
    '''
    if request.method == 'POST':
        params = request.get_json()
        user_id = params.get('user_id', None)
        n_months = int(params.get('n_months', 3))
        if user_id is None:
            data = None
            response = jsonify(data)
            response.status_code = 403
        else:
            all_transactions_list = []
            for token in Token.query.filter_by(user_id=user_id).all():
                # token.item_id and token.access_token
                access_token = token.access_token
                transaction_ids = store_account_transactions(access_token, n_months, user_id)
                all_transactions_list += transaction_ids
            response = jsonify({'number_synced_transactions':len(all_transactions_list)})
            response.status_code = 200
        return response

def get_category_stats(transaction_list):
    category_totals = {}
    for transaction in transaction_list:
        category_list = transaction.get('category_list')
        for category in category_list:
            running_vals = category_totals.get(category, None)
            if running_vals is None:
                running_vals = {'count':0, 'amount':0}
            running_vals['amount'] += transaction['amount']
            running_vals['count'] += 1
            category_totals[category] = running_vals
    # reformat for frontend
    category_total_list = [{'category':key, 'total':value['amount'], 'count':value['count']} for key, value in category_totals.items()]
    return category_total_list

def get_account_transactions_from_firestore(account_id, n_months):
    # get transactions last n months
    now = datetime.now()
    start = (now - timedelta(int(n_months)*365/12))
    print('start:', start, 'end:', now)
    docs = firestore_db.collection('transactions')\
                .where('account_id', '==', account_id,).stream()
    data_list = []
    for doc in docs:
        data = doc.to_dict()
        if (start <= datetime.strptime(data['date'], '%Y-%m-%d') <= now):
            reduced_dict = {}
            reduced_dict['name'] = data['name']
            reduced_dict['amount'] = data['amount']
            reduced_dict['date'] = data['date']
            reduced_dict['category_list'] = data['category']
            data_list.append(reduced_dict)
    return data_list

@app.route('/api/v1/get_category_totals', methods=['GET'])
def get_category_totals():
    '''
    params:
    user_id
    n_months
    '''
    if request.method == 'GET':
        params = request.args
        user_id = params.get('user_id', None)
        n_months = params.get('n_months', 3)
        if user_id is None:
            data = None
            response = jsonify(data)
            response.status_code = 403
        else:
            all_transactions_list = []
            account_snapshot_list = firestore_db.collection('accounts')\
                .where('user_id', '==', user_id,).stream()
            for account_snapshot in account_snapshot_list:
                # pass
                account = account_snapshot.to_dict()
                account_id = account_snapshot.id
                transaction_list = get_account_transactions_from_firestore(account_id, n_months)
                
                all_transactions_list += transaction_list
            category_total_list = get_category_stats(transaction_list)
            # data = sorted(category_total_list, key = lambda x: x['total'], reverse=True)
            response = jsonify(category_total_list)
            response.status_code = 200
        return response

if __name__ == '__main__':
    # access_token = 'access-sandbox-a80895e9-baae-47ed-ae93-6f6801d597a1'
    # extract_liability_summary(access_token =access_token)
    # user_id = 'EIKvpm56NiNPDf07ZFybSgEhFCg2'
    # sync_transactions_temp(user_id, n_months=2)
    # get_category_totals_sample(user_id, n_months=2, request_method='GET')
    app.run(debug=True, host='0.0.0.0')
