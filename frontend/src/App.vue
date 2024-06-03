<template>
  <v-app>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script setup>
import Login from './components/LoginRegister.vue';
import Home from './components/Home.vue';
</script>