<template lang='pug'>
  .box.star-card-box
    h2 {{ item.title }}
    .columns.is-vcentered
      .column.is-narrow
        .box.main-number
          span $200
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
      type: Array,
      required: false,
    },
  },
  data: function () {
    return {
      someThing: '',
    };
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
  .main-number {
    font-size: 50px;
    text-align: center;
    border: solid 1px red;
  }
  .information-text {
      font-weight: 300;
  }
</style>
