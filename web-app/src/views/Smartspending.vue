<template lang='pug'>
  #app
    .container.top-part
      .columns
        .column
          .title Total Spending
          .label Time Period: 1 Month
          graph-pie(
              :width='400'
              :height='400'
              :values='values'
              :names='names'
              :colors='colors'
              :active-index='[ 0, 2 ]'
              :active-event="'click'"
              :show-text-type="'inside'"
              )
          legends(:names='names')
          tooltip(:names='names')
        .column
          .title Saving Suggestions
          .box
            p Try carpooling or planning routes to save money on gas.
          .box
            p Making your own coffee in the morning could cut down your dining cost.
          hr
          .label
            | Total Spent: ${{totalSpent}}
            
</template>
<script>
import { store } from "../store.js";

import VueGraph from 'vue-graph';
import api from '@/services/api.js';

export default {
  components: { VueGraph },
  data: function () {
    return {
      user: store.state.user,
    }
  },
  asyncComputed: {
    categoryList: {
      get () {
        return api.getAccountsSummary(user[0].uid)
      },
      default: 'No fanciness'
    }
  },
  computed: {
    values() {
      // const officersIds = categoryList.map(category => category.value);
      return [ 10, 5, 3, 7 ];
    },
    names() {
      // const officersIds = categoryList.map(category => category.name);
      return [ 'Dining', 'Rent', 'Loans', 'Shopping' ];
    },
    colors() {
      return ["#B1D4E0", "#2E8BC0", "#189AB4", "#145DA0", "#eee"];
    },
    totalSpent() {
      return 1000;
    }
  },
};
</script>

<style>
.top-part{
  margin-top: 2em !important;
}
.title {
  font-size: 2em;
  margin-bottom: 1em;
}
h2 {
  font-size: 1.2em;
  font-weight:500;
}
.container {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 150px;
}
</style>