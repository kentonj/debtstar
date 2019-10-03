<template lang='pug'>
.navigationTop
  nav.navbar.is-nav
    .navbar-brand.navigation-brand
      .navbar-item
         h2 Debt Star
      span.navbar-burger.burger(
          v-bind:class="{ 'is-active': menuIsOpen }"
          @click='toggleMenu'
          data-target='navMenu'
          )
        span
        span
        span
    #navMenu.navbar-menu(
        v-bind:class="{ 'is-active': menuIsOpen }"
        )
      .navbar-end
        router-link.navbar-item(to='/') Dashboard
        router-link.navbar-item(to="/addbank") Manage Accounts
        router-link.navbar-item(to="/login") Login
</template>
<script>
    export default {
      name: 'NavigationBar',
      data: function () {
        return {
          menuIsOpen: false,
        }
      },
      methods: {
        toggleMenu() {
          this.menuIsOpen = !this.menuIsOpen;
        },
      }
    };
</script>
<style scoped>
  .navigation-brand {
    background-color: #eee;
  }
</style>