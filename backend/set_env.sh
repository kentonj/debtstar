#!/bin/bash
echo "setting plaid environment variables"
export PLAID_SECRET=c9985238e890126252341a057c18ed
export PLAID_PUBLIC_KEY=d6c6ee38bb99baa20e364f4179e9e5
export PLAID_PRODUCTS=transactions
export PLAID_COUNTRY_CODES=US,CA,GB,FR,ES
export PLAID_ENV=sandbox
export PLAID_CLIENT_ID=5d9139ec8a49a90012a3676d

echo "setting postgres environment variables"
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=postgres
export POSTGRES_USER=debtstar
export POSTGRES_PASSWORD=supersecretpassword
