<template lang='pug'>
  .home
    dash-board(
      v-if="user"
      )
    .sign-in-message(
      v-if="!user"
      )
      | Sign up or log in
</template>

<script>
import { store } from "../store.js";

import DashBoard from '@/components/DashBoard.vue';

export default {
  name: 'home',
  components: {
    DashBoard,
  },
  data: function () {
    return {
      user: store.state.user,
    }
  },
};
</script>
<style scoped>
  .home {
    padding: 3em;
  }
</style>
