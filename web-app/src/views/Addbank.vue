<template lang='pug'>
  .addBank
    .container
      .columns
        h1 Connect Accounts
      .columns
        | After you click the button, we will connect to your bank account. We use the Plaid platform to do this. Dont worry though, Plaid maintains a SOC 2 compliance and constantly ensures your data is protected via strong TLS encryption and ciphers. No matter how you, and only you, access your data, its for your eyes only.
      .columns.is-pulled-right.add-bank-style
        add-bank-btn(
          env="sandbox"
          publicKey="d6c6ee38bb99baa20e364f4179e9e5"
          clientName="Debt Star"
          product="transactions"
          v-bind="{ onSuccess }"
          ) Open Plaid
      
</template>
<script>
import { store } from "../store.js";

import AddBankBtn from '@/components/AddBankBtn.vue';
import api from '@/services/api.js';

export default {
  components: { AddBankBtn },
  data: function () {
    return {
      userEmail: '',
      userPassword: '',
      user: store.state.user,
    }
  },
  methods: {
    addBankUI() {
      console.log('add bank');
    },
    onSuccess (token) {
      api.connectBank(token, this.userID)
        .then((data) => {
          console.log(data);
        })
      console.log(token)
    },
  },
};
</script>

<style lang="scss" scoped>
h1 {
  font-size: 2em;
  margin-bottom: 1em;
}
.container {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 50px;
}
.add-bank-style {
  font-size: 20px;
  color: #09c;
}
#plaid-link-iframe-1 iframe {
    height: 100% !important;
  }
</style>