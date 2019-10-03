import axios from 'axios';

export default {
  connectBank,
  getSummarizeLiabilities,
};

function connectBank(public_token, user_id ) {
    const params = {
      public_token,
      user_id,
    };
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
      'Authorization': 'authorization',
    };
    const url = 'http://localhost:5000/api/v1/store_access_token';
    return axios.post(url, params, headers)
      .then((responce) => {
        console.log(responce);
      })
}

function getSummarizeLiabilities( user_id ) {
  const params = {
    user_id,
  };
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
    'Authorization': 'authorization',
  };
  const url = 'http://localhost:5000/api/v1/get_liability_summary';
  return axios.get(url, params, headers)
    .then((responce) => {
      console.log(responce);
    })
}
