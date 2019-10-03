<template lang='pug'>
  .dashboard
    .columns
      .column
        h1 {{ userName }}'s Dashboard {{myDebtList}}
      .column.is-narrow
        .budget-box
          .budget-title
            span Amount Under Budget
          .budget-amount
            | ${{ budgetRemaining }}
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
    | See how far a single payment of ${{ dollarsInvested }} will go in {{ investmentYears }} years and {{ investmentMonths }} months when you put it toward a loan or investment!
    .dash-cards(v-for="item in itemList")
      star-card(
        :item="item"
        :term="totalMonths"
        :dollarsInvested="dollars_Invested"
        )
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
      itemList: [
        {
          title: 'Student Debt',
          type: 'debt',
          accumulating_value: .05,
          monthly_payment: 200,
          current_value: 100000,
          original_value: 150000,
          loan_period_remaining: 3,
        },
        {
          title: '401k Retirment Fund',
          type: 'investment',
          accumulating_value: .03,
          current_value: 1200,
          original_value: 1000,
        },
      ],
    }
  },
  computed: {
    userName() {
      return this.user[0].name || null;
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
</style>
