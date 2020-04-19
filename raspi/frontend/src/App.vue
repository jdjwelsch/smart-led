<template>
  <div id="app">
    <H2>LED Jona</H2>
    <SingleLedControl name="led1" :server-ip="server_ip"></SingleLedControl>

    <H2>LED Wohnzimmer</H2>
    <SingleLedControl name="led2" :server-ip="server_ip"></SingleLedControl>
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
  data: function () {
    return {
      server_ip: '192.168.0.9',
    }
  }
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
