# debtstar

Student and consumer debt is a huge problem. Like any problem we believe the first step to solving it is understanding how it works. We created the Debt Star in order to help people understand their spending and visualize how altering their habits a little can translate into big savings for their debts in the future.

# components
- Vue front-end
  - Firebase Authentication and Cloud Firestore
  - Plaid Link for bank authentication
- Flask back-end
  - Flask and Postgres running inside docker container
  - Plaid API interaction - token exchange, accessing resources
  - Local postgres DB for storing access tokens
  - Read/Writes to/from Cloud Firestore
