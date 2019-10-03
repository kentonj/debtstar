<template lang='pug'>
  .box.star-card-box
    h2 {{ item.title }}
    .columns.is-vcentered
      .column.is-narrow(v-if="item.type === 'investment'")
        .box.main-number-invest
          span.main-number-font ${{ totalEarnedOverTime }}
          p Projected Earnings
      .column.is-narrow(v-else)
        .box.main-number-debt
          span.main-number-font ${{ totalEarnedOverTime }}
          p Projected Savings
      .column
        .label Current Value:
          span.information-text ${{ item.current_value }}
        .label Interest:
          span.information-text {{ item.accumulating_value }}
        .label(v-if="item.monthly_payment") Monthly Payment:
          span.information-text ${{ item.monthly_payment }}
      .column.is-narrow
        b-button.theme-dark-blue.has-text-white(
          @click="makePayment"
          ) Make Payment
</template>
<script>
export default {
  props: {
    item: {
      type: Object,
      required: false,
    },
    term: {
      type: Number,
      default: 0,
    },
    dollarsInvested: {
      type: Number,
      default: 0,
    },
  },
  data: function () {
    return {
      someThing: '',
    };
  },
  computed: {
    totalEarnedOverTime() {
      const fv = this.dollarsInvested * (1 + this.item.accumulating_value / 12) ** (this.term);
      const val = Number(fv) - this.dollarsInvested;
      const formatted_val = val.toFixed(2);
      return formatted_val;
    },
  },
  methods: {
    makePayment() {
      //open a modal
    },
  }
};
</script>
<style scoped>
  h2 {
    font-weight: 700;
    margin-bottom: 5px;
    font-size: 20px;
  }
  .theme-dark-blue {
    background-color: #1B196B;
  }
  .star-card-box {
    margin-top: 1em;
    text-align: left;
  }
  .main-number-invest {
    text-align: center;
    border: solid 1px green;
  }
  .main-number-debt {
    text-align: center;
    border: solid 1px red;
  }
  .main-number-font {
    font-size: 50px;
  }
  .information-text {
      font-weight: 300;
  }
</style>
