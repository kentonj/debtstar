<template lang='pug'>
  .addBankBtn
    plaid-link(
      env="sandbox"
      publicKey="d6c6ee38bb99baa20e364f4179e9e5"
      clientName="Debt Star"
      product="transactions"
      v-bind="{ onSuccess }"
      ) Open Plaid Link {{user}}
</template>
<script>
import { store } from "../store.js";

import PlaidLink from 'vue-plaid-link'
import api from '@/services/api.js';

export default {
  components: { PlaidLink },
  data: function () {
    return {
      userEmail: '',
      userID: store.state.user[0].uid,
    }
  },
  methods: {
    onSuccess (token) {
      api.connectBank(token, this.userID)
        .then((data) => {
          console.log(data);
        })
      console.log(token)
    },
  },
};
</script>
<style scoped>
 .addBankBtn {
   z-index: 99999;
 }
</style>
