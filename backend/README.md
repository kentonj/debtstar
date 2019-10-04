# Debtstar Backend
The backend consists of a Python Flask server running inside of a docker container, along with a local postgres DB for storing access tokens from Plaid. The Flask server has a number of endpoints that the front end interacts with. These include `store_access_token`, `get_accounts_summary` and other routes to interact and retrieve data from the Plaid client. The backend also reads/writes from firestore db.

# Deployment
- Before starting the container, the following environment variables must be set:
  - POSTGRES_HOST
  - POSTGRES_PORT
  - POSTGRES_DB
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - PLAID_CLIENT_ID
  - PLAID_SECRET
  - PLAID_PUBLIC_KEY
  - PLAID_ENV
  - PLAID_PRODUCTS
  - PLAID_COUNTRY_CODES
- To connect to firestore db, a key.json file must be downloaded from firebase, and placed in the `debtstar/backend` directory.
- To run the backend, cd into `debtstar/backend` and run `docker-compose up`, which will build the flask and postgres services. Flask and Postgres are mapped to their regular ports, 5000 and 5432, respectively.
- Point the front-end to use `http://YOUR_FLASK_SERVER_URL:5000/api/v1` as the base url for all routes.

