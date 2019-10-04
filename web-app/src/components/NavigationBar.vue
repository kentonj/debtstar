<template lang='pug'>
.navigationTop
  nav.navbar.is-nav
    .navbar-brand.navigation-brand
      .navbar-item
        h3 Debt Star
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
        router-link.navbar-item(to='/') Debt Annihilator
        router-link.navbar-item(to="/smartspending") Smart Spending
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
<style>
  h3 {
    color: #2A96C9 !important;
    font-size: 25px;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
  }
  img {
    max-width:50px !important;
  }
</style>