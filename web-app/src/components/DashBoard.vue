<template lang='pug'>
  .dashboard
    .columns
      .column
        .title {{ userName }}'s Debt Annihilator
    .has-bank(v-if="itemList2.length")
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
      span.is-thin See how far
        span.is-fat &nbsp; a single payment of ${{ dollarsInvested }} today
          span.is-thin &nbsp; will go in {{ investmentYears }} years and {{ investmentMonths }} months when you put it toward a loan or investment!
      .dash-cards(
        v-for="item in itemList2")
        star-card(
          :item="item"
          :term="totalMonths"
          :dollarsInvested="dollars_Invested"
          )
    .set-account-message(v-else)
      .welcome-text
        | Welcome,
      h2 Looks like you do not have a bank account set up with Debt Star
      b-button(@click="goToSetUp") Set Up Account
</template>
<script>
import { store } from "../store.js";

import StarCard from '@/components/StarCard.vue';
import api from '@/services/api.js';

export default {
  components: {
    StarCard,
  },
  data: function () {
    return {
      user: store.state.user,
      myDebtList: store.state.userDebt,
      investmentYears: 0,
      investmentMonths: 0,
      dollarsInvested: 0,
      under_budget: 100,
    }
  },
  computed: {
    userName() {
      return this.user[0] ? this.user[0].name : 'User';
    },
    itemList2() {
      return this.myDebtList[0] ? this.myDebtList[0].data : [];
    },
    dollars_Invested() {
      return Number(this.dollarsInvested);
    },
    totalMonths() {
      var y = this.investmentYears * 12;
      var total = y + Number(this.investmentMonths);
      return total;
    },
    budgetRemaining() {
      return this.under_budget - this.dollars_Invested;
    }
  },
  methods: {
    goToSetUp() {
      this.$router.push({ name: 'addbank' });
    },
  }
};
</script>

<style lang="scss" scoped>
.title {
  font-size: 2em;
  margin-bottom: 1em;
}
.welcome-text {
  font-size: 2em;
  font-family: 'Oswald', sans-serif;
  font-weight: 700;
  color: #2A96C9;
}
.container {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 50px;
}
.time-inputs {
  width: 20%;
}
.budget-box {
  width: 100%;
  border-radius: 10px;
  box-shadow: 0 2px 3px rgba(10, 10, 10, 0.1), 0 0 0 1px rgba(10, 10, 10, 0.1);
}
.budget-title {
  border-radius: 10px 10px 0px 0px;
  padding: 5px 10px;
  box-shadow: 0 2px 3px rgba(10, 10, 10, 0.1), 0 0 0 1px rgba(10, 10, 10, 0.1);
  background-color: #1B196B;
  color: #fff;
}
.budget-amount {
  text-align: center;
  font-size: 30px;
}
.theme-dark-blue {
    background-color: #1B196B;
}
.is-thin {
  font-weight: 400;
  color: #000;
}
.is-fat {
  font-weight: 700;
  color: #2A96C9;
}
</style>
