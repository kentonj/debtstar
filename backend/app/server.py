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
import sys

category_dict = {
        'Travel':["Travel", "Airlines and Aviation Services", "Car Service", "Ride Share"],
        'Payments':["Payment"],
        'Food':["Food and Drink", "Restaurants", "Coffee Shop"], 
        'Shopping':["Shops", "Sporting Goods"],
        'Recreation':["Recreation","Gyms and Fitness Centers"],
        'Account':["Credit Card", "Transfer", "Debit", "Deposit", "Credit"],
        'Other':[]
    }

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

    print('exchanging access token', file=sys.stderr)
    try:
        exchange_response = plaid_client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        response = jsonify(format_error(e))
        response.status_code = 403
        return response
    access_token = exchange_response.get('access_token')
    item_id = exchange_response.get('item_id')
    
    # store token in local database
    print('storing token in local database', file=sys.stderr)
    token = Token(user_id=user_id, item_id=item_id, public_token=public_token, access_token=access_token)
    token.upsert()

    print('writing item without access_token to firestore', file=sys.stderr)
    item_collection = SuperCollection(firestore_db, 'items', 'item_id')
    exchange_response.pop('access_token')
    exchange_response['user_id'] = user_id
    item_collection.write(exchange_response)

    print('getting all accounts and storing to filestore', file=sys.stderr)
    # now also store all accounts from that item in firestore too
    accounts_response = plaid_client.Accounts.get(access_token=access_token)
    account_collection = SuperCollection(firestore_db, 'accounts', 'account_id')
    for account in accounts_response['accounts']:
        account['user_id'] = user_id
        account['item_id'] = item_id
        print('storing this account:', account)
        account_collection.write(account)
    
    print('getting all liabilities and storing to filestore', file=sys.stderr)
    liability_summary_list = extract_liability_summary(access_token)
    liability_collection = SuperCollection(firestore_db, 'liabilities')
    for i, liability in enumerate(liability_summary_list):
        liability['user_id'] = user_id
        liability['item_id'] = item_id
        print('storing this liability:', liability)
        liability_collection.write(liability)
    print('{} liabilities have now been stored'.format(i), file=sys.stderr)
    data = {'item_id':item_id}
    # response.status = 200
    response = jsonify(data)
    response.status_code = 200
    return response

def extract_liability_summary(access_token):
    print('extracting liabilities:', file=sys.stderr)
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
        print('CALLING /api/v1/get_accounts_summary for user_id={}'.format(user_id), file=sys.stderr)
        if user_id is None:
            data = None
            response = jsonify(data)
            response.status_code = 403
        else:
            print('Initializing liabilities collection', file=sys.stderr)
            liabilities_collection = SuperCollection(firestore_db, 'liabilities')
            print('successfully initialized liabilities collection, calling .get_by_user', file=sys.stderr)
            all_accounts_list = liabilities_collection.get_by_user(user_id)
            print('got account (liabilities) list from .get_by_user, packagin json response', file=sys.stderr)
            response = jsonify(all_accounts_list)
            response.status_code = 200
        print('heres your response from /api/v1/get_accounts_summary:{}'.format(response.status_code), file=sys.stderr)
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
    transactions_collection = SuperCollection(db=firestore_db,
                                                collection='transactions',
                                                pk_col='transaction_id')
    keys_list = []
    print('got transactions response from plaid client', file=sys.stderr)
    all_transactions = transactions_response['transactions']
    print('all transactions before adding user_id:{}'.format(len(all_transactions)), file=sys.stderr)
    all_transactions_list = []
    for transaction in all_transactions:
        transaction['user_id'] = user_id
        all_transactions_list.append(transaction)
    print('writing all transactions to firestore non-batch style:{}'.format(len(all_transactions_list)), file=sys.stderr)
    # transactions_collection.batchupdate(all_transactions_list)
    for transaction in all_transactions_list:
        transactions_collection.update(transaction)
    print('last transaction written with nonbatch: {}'.format(all_transactions_list[-1]), file=sys.stderr)
    print('DONE writing all transactions to firestore nonbatch style', file=sys.stderr)
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
            # all_transactions_list = []
            # print('starting to sync transactions', file=sys.stderr)
            # all_transactions = Token.query.filter_by(user_id=user_id).all()
            # for i, token in enumerate(all_transactions):
            #     print('syncing from item: {}/{}'.format(i,len(all_transactions)), file=sys.stderr)
            #     # token.item_id and token.access_token
            #     access_token = token.access_token
            #     transaction_ids = store_account_transactions(access_token, n_months, user_id)
            #     all_transactions_list += transaction_ids
            # print('packaging up JSON', file=sys.stderr)
            # response = jsonify({'number_synced_transactions':len(all_transactions_list)})
            # response.status_code = 200
            print('doing nothing with this endpoint', file=sys.stderr)
            response = jsonify(None)
            response.status_code = 200
        return response

def consolidate_categories(category_list):
    print('got into consolidate categories', file=sys.stderr)
    first_category = category_list[0]
    for key, value_list in category_dict.items():
        if first_category in value_list:
            print('got out of consolidate categories', file=sys.stderr)
            return key
        else:
            pass
    print('got out of consolidate categories', file=sys.stderr)
    return 'Other'


def get_category_stats(transaction_list):
    print('category_dict:{}'.format(category_dict), file=sys.stderr)
    category_totals = {key:{'count':0, 'amount':0} for key in category_dict.keys()}
    print('category totals before addition:{}'.format(category_totals), file=sys.stderr)
    for transaction in transaction_list:
        category_list = transaction.get('category_list')
        # for category in category_list:
        #     running_vals = category_totals.get(category, None)
        #     if running_vals is None:
        #         running_vals = {'count':0, 'amount':0}
        #     running_vals['amount'] += transaction['amount']
        #     running_vals['count'] += 1
        #     category_totals[category] = running_vals
        category = consolidate_categories(category_list)
        print('getting running_vals', file=sys.stderr)
        running_vals = category_totals.get(category, None)
        if running_vals is None:
            running_vals = {'count':0, 'amount':0}
        print('adding to running_vals', file=sys.stderr)
        running_vals['amount'] += transaction['amount']
        running_vals['count'] += 1
        print('category_totals[{}]'.format(category), file=sys.stderr)
        category_totals[category] = running_vals
    print('category list:{}'.format(category_totals), file=sys.stderr)
    category_total_list = [{'category':key, 'total':value['amount'], 'count':value['count']} for key, value in category_totals.items()]
    print('category total list:{}'.format(category_total_list), file=sys.stderr)    
    return category_total_list

def get_account_transactions_from_firestore(user_id, n_months):
    # get transactions last n months
    now = datetime.now()
    start = (now - timedelta(int(n_months)*365/12))
    print('start:', start, 'end:', now)
    docs = firestore_db.collection('transactions')\
                .where('user_id', '==', user_id,).stream()
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

def get_all_transactions(user_id, n_months):
    now = datetime.now()
    start = (now - timedelta(int(n_months)*365/12))
    all_tokens = Token.query.filter_by(user_id=user_id).all()
    all_transactions_list = []
    
    for token in all_tokens:
        access_token = token.access_token
        transactions_response = plaid_client.Transactions.get(access_token, 
                                                                start_date=start.strftime('%Y-%m-%d'),
                                                                end_date=now.strftime('%Y-%m-%d'))
        for transaction in transactions_response['transactions']:
            reduced_dict = {}
            reduced_dict['name'] = transaction['name']
            reduced_dict['amount'] = transaction['amount']
            reduced_dict['date'] = transaction['date']
            reduced_dict['category_list'] = transaction['category']
            all_transactions_list.append(reduced_dict)
    return all_transactions_list

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
        print('starting call to /api/v1/get_category_totals with params:{}'.format(params), file=sys.stderr)
        if user_id is None:
            data = None
            response = jsonify(data)
            response.status_code = 403
        else:
            # all_transactions_list = []
            # account_snapshot_list = firestore_db.collection('accounts')\
            #     .where('user_id', '==', user_id,).stream()
            all_transactions_list = get_all_transactions(user_id, n_months)
            print('got all transactions, getting the stats', file=sys.stderr)
            # # all_transactions_list += transaction_list
            category_total_list = get_category_stats(all_transactions_list)
            # data = sorted(category_total_list, key = lambda x: x['total'], reverse=True)
            data = category_total_list
            response = jsonify(data)
            response.status_code = 200
        print('heres your response:{}'.format(response.status_code), file=sys.stderr)
        print('heres your full response:{}'.format(response), file=sys.stderr)
        return response

if __name__ == '__main__':
    # access_token = 'access-sandbox-a80895e9-baae-47ed-ae93-6f6801d597a1'
    # extract_liability_summary(access_token =access_token)
    # user_id = 'EIKvpm56NiNPDf07ZFybSgEhFCg2'
    # sync_transactions_temp(user_id, n_months=2)
    # get_category_totals_sample(user_id, n_months=2, request_method='GET')
    app.run(debug=True, host='0.0.0.0')
