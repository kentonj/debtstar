<template lang='pug'>
  .app
    navigation-bar
    router-view
</template>
<script>
import NavigationBar from '@/components/NavigationBar.vue';

export default {
  components: {
    NavigationBar,
  },
};
</script>
<style lang="scss" scoped>
.app {
  font-family: 'Montserrat', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  text-align: center;
}
h1 {
  font-size: 2em;
}
.container {
  margin-left: 5%;
  margin-right: 5%;
}
.theme-dark-blue {
  background-color: #1B196B;
  color: #fff;
}
#plaid-link-iframe-1 iframe {
    height: 100% !important;
  }
</style>
