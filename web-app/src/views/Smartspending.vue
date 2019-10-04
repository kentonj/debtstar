<template lang='pug'>
  #app
    .container.top-part
      .columns
        .column
          .title Total Spending
          .label Time Period: 1 Month
          graph-pie(
              :width='500'
              :height='500'
              :values='values'
              :padding-top="100"
              :padding-bottom="100"
              :padding-left="100"
              :padding-right="100"
              :names='names'
              :colors='colors'
              :active-index='[ 0, 2 ]'
              :active-event="'click'"
              :show-text-type="'outside'"
              )
          legends(:names='names')
          tooltip(:names='names')
        .columns
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
      userSpending: store.state.userSpending,
      categoryList: [],
    }
  },
  methods: {
    openStuff() {
      api.getCategoryTotals(this.user[0].uid)
        .then((data) => {
          this.categoryList = data.data;
       });
    },
  },
  mounted(){
    this.openStuff();
  },
  computed: {
    values() {
      const total = this.categoryList.map(cat => cat.total);
      return total;
    },
    names() {
      const category = this.categoryList.map(cat => cat.category);
      return category;
    },
    colors() {
      return ["#B1D4E0", "#2E8BC0", "#189AB4", "#145DA0", "#eee","#B1D4E0", "#2E8BC0", "#189AB4", "#145DA0", "#eee"];
    },
    totalSpent() {
      const totalS = this.values.reduce((a, b) => a + b, 0);
      const formatTotal = Number(totalS).toFixed(2);
      return formatTotal;
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