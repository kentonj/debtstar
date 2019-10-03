<template lang='pug'>
  .dashboard
    h1 {{ userName }}'s Dashboard
    .columns
      .column.is-narrow
        b-field(label="Years")
          b-input(type="number", v-model="investmentYears" placeholder="years")
      .column.is-narrow
        b-field(label="Months")
          b-input(type="number", v-model="investmentMonths" placeholder="months")
      .column.is-narrow
        b-field(label="Dollars")
          b-input(type="number", v-model="dollarsInvested" placeholder="Payment")
    | See how far ${{ dollarsInvested }} will go in {{ investmentYears }} years and {{ investmentMonths }} months when you put it toward a loan or investment!
    star-card
</template>
<script>
import { store } from "../store.js";

import StarCard from '@/components/StarCard.vue';

export default {
  name: 'dashBoard',
  components: {
    StarCard,
  },
  data: function () {
    return {
      user: store.state.user,
      investmentYears: 0,
      investmentMonths: 0,
      dollarsInvested: 0,
    }
  },
  computed: {
    userName() {
      return this.user[0].name || null;
    },
    totalMonths() {
      var y = this.investmentYears * 12;
      var total = y + Number(this.investmentMonths);
      return total;
    },
  }
};
</script>

<style lang="scss" scoped>
h1 {
  font-size: 2em;
  margin-bottom: 1em;
}
.container {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 50px;
}
.time-inputs {
  width: 20%;
}
</style>
