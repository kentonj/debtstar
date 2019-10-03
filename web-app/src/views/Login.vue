<template lang='pug'>
  .login
    .box.sign-up-box
      b-field(label="Email")
        b-input(type="email", v-model="userEmail", maxlength="40")
      b-field(label="Password")
        b-input(type="password", v-model="userPassword", password-reveal="")
      b-button(@click="loginUser") Login
</template>
<script>
import firebase from 'firebase/app';
import 'firebase/firestore';
import { store } from "../store.js";

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
    }
  },
};
</script>
<style scoped>
  .sign-up-box {
    max-width: 600px;
    min-width: 400px;
    width: 50%;
    margin: 2em auto;
  }
</style>
