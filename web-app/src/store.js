import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export const store = {
  state: {
    user: [],
    userDebt: [],
  },
  addUserData(userInfo) {
    this.state.user.push(userInfo);
  },
  addUserDebt(data) {
    console.log('here');
    console.log(data);
    this.state.userDebt.push(data);
  },
};
