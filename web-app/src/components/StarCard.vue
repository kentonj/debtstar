<template lang='pug'>
  .box.star-card-box(v-if="item.is_debt")
    h3 {{ item.name }}
    .columns.is-vcentered
      .column.is-narrow(v-if="!item.is_debt")
        .box.main-number-invest
          span.main-number-font ${{ totalEarnedOverTime }}
          P Value of ${{ dollarsInvested }}
          p with savings over {{this.term}} months
      .column.is-narrow(v-else)
        .box.main-number-debt
          span.main-number-font ${{ totalEarnedOverTime }}
          P Debt reduced by ${{ dollarsInvested}}
          p over {{this.term}} months
      .column
        h2 Current
        .label.has-text-grey-dark Current Value:
          span.information-text &nbsp; ${{ currentBalanceFormatted }}
        .label.has-text-grey-dark Interest:
          span.information-text &nbsp; {{ item.interest * 100 }}%
        .label.has-text-grey-dark(v-if="item.minimum_payment") Monthly Payment:
          span.information-text &nbsp; ${{ formattedPayment }}
        //- .label.has-text-grey-dark Interest from Payment:
        //-   span.information-text &nbsp; ${{ currentMonthlyInterest }}
      .column 
        h2 Projection In {{ this.term }} Months
        .label.has-text-grey-dark(v-if="item.is_debt") Value Remaining:
          span.information-text &nbsp; ${{ futureValueWithPayments }}
        .label.has-text-grey-dark Interest:
          span.information-text &nbsp; {{ item.interest * 100 }}%
        .label.has-text-grey-dark(v-if="item.minimum_payment") Monthly Payment:
          span.information-text &nbsp; ${{ formattedPayment }}
        //- .label.has-text-grey-dark Interest from Payment:
        //-   span.information-text &nbsp; ${{ futureMonthlyInterest }}
      .column.is-narrow
        b-button.theme-dark-blue.has-text-white(
          @click="makePayment"
          disabled="true"
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
    currentBalanceFormatted() {
      return Number(this.item.current_balance).toFixed(2);
    },
    formattedPayment() {
      return Number(this.item.minimum_payment).toFixed(2);
    },
    numberCurrentBalance() {
      return Number(this.item.current_balance);
    },
    numberTerm() {
      return Number(this.term);
    },
    numberDollarInvested() {
      return this.dollarsInvested;
    },
    numberInterest() {
      return Number(this.item.interest);
    },
    numberMinPayment() {
      return Number(this.item.minimum_payment);
    },
    totalEarnedOverTime() {
      const fv = this.dollarsInvested * (1 + this.item.interest / 12) ** (this.numberTerm);
      const val = Number(fv);
      const formatted_val = val.toFixed(2);
      return formatted_val;
    },
    futureValueWithPayments() {
      const original_value_fv = (this.numberCurrentBalance * ((1 + this.numberInterest / 12) ** this.numberTerm));
      const monthly_payment_fv = ((((1 + this.numberInterest / 12) ** this.term) -1 ) / (this.numberInterest/12)) * this.numberMinPayment;
      const future_val_with_payments = original_value_fv - monthly_payment_fv;
      const dollars_invested_fv = (this.numberDollarInvested * ((1 + this.numberInterest / 12) ** this.numberTerm));
      const future_val_with_extra_dollars = future_val_with_payments - dollars_invested_fv;
      const formatFV = Number(future_val_with_extra_dollars).toFixed(2);
      return formatFV;
    },
    projectedValue() {
      const val = this.totalEarnedOverTime + (this.term * this.item.minimum_payment);
      const val2 = this.item.current_balance - val;
      return Number(val2).toFixed(2);
    },
    futureMonthlyInterest() {
      const val = (this.projectedValue * (this.item.interest / 12));
      return Number(val).toFixed(2);
    },
    currentMonthlyInterest() {
      const val = (this.item.current_balance * (this.item.interest / 12));
      return Number(val).toFixed(2);
    }
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
  h3 {
    font-weight: 700;
    margin-bottom: 5px;
    font-size: 20px;
    color: #1B196B !important;
    font-family: 'Montserrat', Helvetica, Arial, sans-serif;
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
  }
  .main-number-font {
    font-size: 50px;
  }
  .information-text {
      font-weight: 300;
  }
</style>
