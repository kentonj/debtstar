import axios from 'axios';

export default {
  connectBank,
  getAccountsSummary,
  syncTransactions,
  getCategoryTotals,
};

function connectBank(public_token, user_id ) {
    const params = {
      public_token,
      user_id,
    };
    const url = 'http://localhost:5000/api/v1/store_access_token';
    return axios.post(url, params)
      .then(response => response)
}

function getAccountsSummary(user_id) {
  const config = {
    params: {
      user_id
    }
  };
  const url = 'http://localhost:5000/api/v1/get_accounts_summary';
  return axios.get(url, config)
    .then(response => response)
}

function syncTransactions(user_id) {
  const params = {
    user_id,
    n_months: 2,
  };
  const url = 'http://localhost:5000/api/v1/sync_transactions';
  return axios.post(url, params)
    .then(response => response)
}

function getCategoryTotals(user_id) {
  const config = {
    params: {
      user_id,
      n_months: 2,
    }
  };
  const url = 'http://localhost:5000/api/v1/get_category_totals';
  return axios.get(url, config)
    .then(response => response)
}
