<template lang='pug'>
  .signup
    .box.sign-up-box
      .columns
        .column
          h3 Sign Up
          br
          .columns
            .column
              b-input(v-model="displayName", placeholder="Full Name", maxlength="40")
          .columns
            .column
              b-input(type="email", v-model="userEmail", placeholder="Email", maxlength="40")
          .columns
            .column
              b-input(type="password", v-model="userPassword", placeholder="Password", password-reveal="")
          b-button.has-text-white.theme-dark-blue(@click="signUpNewUser") Sign Up
        .column
          .login-img
            img(
              src="../assets/logo.svg"
              )
            b-button.has-text-white.theme-dark-blue(@click="loginUser") Log In
</template>
<script>
import firebase from 'firebase/app';
import 'firebase/firestore';

export default {
  data: function () {
    return {
      displayName: '',
      userEmail: '',
      userPassword: '',
    }
  },
  methods: {
    signUpNewUser() {
      firebase.auth().createUserWithEmailAndPassword(this.userEmail, this.userPassword)
        .then((user) => {
          firebase.firestore().collection('users').doc(user.user.uid).set({
            email: user.user.email,
            name: this.displayName,
            uid: user.user.uid,
          });
        })
        .then(function() {
          this.$router.push({ name: 'login' });
        });
    },
    loginUser() {
      this.$router.push({ name: 'login' });
    },
  },
};
</script>
<style scoped>
  h3 {
    color: #2A96C9;
    font-size: 30px;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
  }
  .sign-up-box {
    max-width: 600px;
    min-width: 400px;
    width: 50%;
    margin: 2em auto;
    text-align: center;
  }
  .theme-dark-blue {
    background-color: #1B196B;
  }
</style>
