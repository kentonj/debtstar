import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export const store = {
  state: {
    user: [],
  },
  addUserData(userInfo) {
    this.state.user = [];
    this.state.user.push(userInfo);
  }
};
