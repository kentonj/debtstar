import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export const store = {
  state: {
    user: [],
    userDebt: [],
    userSpending: [],
  },
  addUserData(userInfo) {
    this.state.user.push(userInfo);
  },
  addUserDebt(data) {
    this.state.userDebt.push(data);
  },
  addUserSpending(data) {
    this.state.userSpending.push(data);
  }
};
