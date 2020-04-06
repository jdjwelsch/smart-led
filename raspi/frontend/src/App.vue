<template>
  <div id="app">
    <SingleLedControl name="led1"></SingleLedControl>
  </div>
</template>

<script>

import 'vue-range-slider/dist/vue-range-slider.css'
import SingleLedControl from "./components/SingleLedControl";

// TODO: get devices from backend
// TODO: construct controls for each device
// TODO: establish socket communication

export default {
  name: 'App',
  components: {
    SingleLedControl
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
