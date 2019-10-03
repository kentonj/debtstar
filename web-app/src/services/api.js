import axios from 'axios';

export default {
  connectBank,
  getSummarizeLiabilities,
  postTest,
  getTest,
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
  // const headers = {
  //   'Access-Control-Allow-Origin': '*',
  //   'Content-Type': 'application/json',
  //   'Authorization': 'authorization',
  // };
  return axios.get(`http://localhost:5000/api/v1?users=${user_id}/get_accounts_summary`)
    .then((responce) => {
      console.log(responce);
    })
}

function postTest(user_id) {
  const params = {
    user_id,
  };
  const url = 'http://localhost:5000/post_test';
  return axios.post(url, params)
    .then(response => response)
}

function getTest(user_id) {
  const config = {
    params: {
      user_id
    }
  };
  const url = 'http://localhost:5000/get_test';
  return axios.get(url, config)
    .then(response => response)
}
