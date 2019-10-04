<template lang='pug'>
  .login
    .box.sign-up-box
      .columns.is-vcentered
        .column
          h3 WELCOME BACK
          br
          .columns
            .column
              b-input(type="email", v-model="userEmail", placeholder="Email", maxlength="40")
          .columns
            .column
              b-input(type="password", v-model="userPassword", placeholder="Password", password-reveal="")
          .columns
            .column
              b-button.has-text-white.theme-dark-blue(@click="loginUser") Login
        .column
           .login-img
            img(
              src="../assets/logo.svg"
            )
            b-button.has-text-white.theme-dark-blue(@click="signUp") Sign Up
</template>
<script>
import firebase from 'firebase/app';
import 'firebase/firestore';
import { store } from "../store.js";
import api from '@/services/api.js';


export default {
  data: function () {
    return {
      userEmail: '',
      userPassword: '',
      user: store.state.user,
    }
  },
  methods: {
    loginUser() {
      firebase.auth().signInWithEmailAndPassword(this.userEmail, this.userPassword)
        .then((user) => {
          this.getUser(user.user.uid);
          this.setUserAccounts(user.user.uid);
          this.syncTransactions(user.user.uid);
        });
    },
    getUser(userId) {
      firebase.firestore().collection('users').doc(userId).get()
        .then((userDoc) => {
          const getData = userDoc.data();
          store.addUserData(getData);
          this.$router.push({ name: 'home' });
        })
        .catch((e) => {
          alert(e);
        })
    },
    setUserAccounts(userId) {
      api.getAccountsSummary(userId)
        .then((data) => {
          console.log(data);
          store.addUserDebt(data);
        });
    },
    syncTransactions(userId) {
      api.syncTransactions(userId)
        .then(() => {
          api.getCategoryTotals(userId)
        });
    },
    signUp() {
      this.$router.push({ name: 'signup' });
    }
  },
};
</script>
<style>
  h3 {
    color: #2A96C9;
    font-size: 30px;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
  }
  img {
    max-width:400px !important;
  }
  .sign-up-box {
    max-width: 600px;
    min-width: 400px;
    width: 50%;
    margin: 2em auto;
    text-align: center;
  }
  .theme-dark-blue {
    background-color: #1B196B !important;
  }
  
</style>
