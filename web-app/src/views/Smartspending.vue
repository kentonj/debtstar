<template lang='pug'>
  #app
    .container
      .columns
        .column
          .title Total Spending
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
            p suggestion
          .box
            p suggestion 2
          hr
          .label
          | Total Spent: $2,000
</template>
<script>
import { store } from "../store.js";

import VueGraph from 'vue-graph';
import api from '@/services/api.js';

export default {
  components: { VueGraph },
  data: function () {
    return {
      values: [ 10, 5, 3, 7 ],
      names: [ 'Dining', 'Rent', 'Loans', 'Shopping' ],
      colors: ["#000", "#333", "#999", "#bbb", "#eee"],
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
  }
};
</script>

<style>
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
  margin-top: 50px;
}
</style>