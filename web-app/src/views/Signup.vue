<template lang='pug'>
  .signup
    .box.sign-up-box
      b-field(label="Name")
        b-input(v-model="displayName", maxlength="40")
      b-field(label="Email")
        b-input(type="email", v-model="userEmail", maxlength="40")
      b-field(label="Password")
        b-input(type="password", v-model="userPassword", password-reveal="")
      b-button(@click="signUpNewUser") Sign Up
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
