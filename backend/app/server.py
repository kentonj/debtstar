from flask import Flask, jsonify, request
from flask_cors import CORS


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/get_test', methods=['GET'])
def get_test():
    parameters = request.get_json()
    print('method: {}, parameters: {}'.format(request.method, parameters))
    if request.method == 'GET':
        post_data = request.get_json()
        if post_data is None:
            return jsonify({'sampledata':None})
        user_id = post_data.get('user_id')
        data = {'user_id':user_id}
    else:
        data = {'sampledata':None}
    return jsonify(data)

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
    else:
        data = {'sampledata':None}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')