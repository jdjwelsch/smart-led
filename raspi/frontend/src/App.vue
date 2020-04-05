<template>
  <div id="app">
    <button @click='toggle()'>On/Off</button>
    <span v-show='status'>LED on</span>
    <span v-show='!status'>LED off</span>

    <range-slider
      class="slider"
      min="0"
      max="100"
      step="1"
      v-model="sliderValue">
    </range-slider>

  </div>
</template>

<script>
import axios from 'axios';
import RangeSlider from 'vue-range-slider'
import 'vue-range-slider/dist/vue-range-slider.css'


export default {
  name: 'App',
  components: {
    RangeSlider
    // HelloWorld
  },
  data: function() {
    return {
      status: false,
      sliderValue: 50
    }
  },
  methods: {
    toggle: function() {
      this.status = !this.status;
      this.switch_led(this.status);
    },
    switch_led: function(state) {
      const path = 'http://192.168.0.78:5000/devices/led1';
      const data_on = {'r': 255, 'g': 0, 'b': 0};
      const data_off = {'r': 0, 'g': 0, 'b': 0};

      if (state) {
        axios.put(path, data_on);
        console.log(data_on);

      }

      if (!state) {
        axios.put(path, data_off);
      }
    },
    set_led_brightness: function(val) {
      const data_bright = {'r': 255*(1 - val/100) , 'g': 0, 'b': 0};
      console.log(data_bright);
      const path = 'http://192.168.0.78:5000/devices/led1';
      axios.put(path, data_bright);
    }

  },
  watch: {
    sliderValue: function(val) {
      this.set_led_brightness(val);
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
