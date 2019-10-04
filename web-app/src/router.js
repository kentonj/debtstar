import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import Login from './views/Login.vue';
import Signup from './views/Signup.vue';
import Addbank from './views/Addbank.vue';
import Smartspending from './views/Smartspending.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/Login',
      name: 'login',
      component: Login,
    },
    {
      path: '/Signup',
      name: 'signup',
      component: Signup,
    },
    {
      path: '/Addbank',
      name: 'addbank',
      component: Addbank,
    },
    {
      path: '/Smartspending',
      name: 'smartspending',
      component: Smartspending,
    },
  ],
});
