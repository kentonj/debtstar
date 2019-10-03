import axios from 'axios';

export default {
  connectBank,  
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
    const url = 'http://3.15.181.248:443/api/v1/store_access_token';
    return axios.post(url, params, headers)
      .then((responce) => {
        console.log(responce);
      })
}
