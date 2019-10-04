import Vue from 'vue';
import firebase from 'firebase';
import App from './App.vue';
import router from './router';
import store from './store';
import Buefy from 'buefy';
import 'buefy/dist/buefy.css'
import AsyncComputed from 'vue-async-computed'
import VueGraph from 'vue-graph'
 
Vue.use(VueGraph)
Vue.use(Buefy)
Vue.use(AsyncComputed);

const firebaseConfig = {
  apiKey: "AIzaSyCTPNh8MidIXB0vJQTp1aG1leI0tgDogQI",
  authDomain: "debt-star.firebaseapp.com",
  databaseURL: "https://debt-star.firebaseio.com",
  projectId: "debt-star",
  storageBucket: "debt-star.appspot.com",
  messagingSenderId: "806426407105",
  appId: "1:806426407105:web:81716adead2379cd8f2440"
};

firebase.initializeApp(firebaseConfig);
Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');
