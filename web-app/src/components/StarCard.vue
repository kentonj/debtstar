<template lang='pug'>
  .box.star-card-box
    h2 Student Loan Debt from debt guy
    .columns
      .column.is-narrow
        .box.main-number
          span $200
      .column
        .label Total:
          span.information-text $20,000
        .label Interest:
          span.information-text 5%
        .label monthly Payment:
          span.information-text $20
        .label Loan Period:
          span.information-text 30 Years
      .column
        b-button Action
</template>
<style scoped>
  h2 {
    font-weight: 400;
    font-size: 16px;
  }
  .star-card-box {
    margin-top: 1em;
    text-align: left;
    border: solid 1px red;
  }
  .main-number {
      font-size: 50px;
      text-align: center;
  }
  .information-text {
      font-weight: 300;
  }
</style>
