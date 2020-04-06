<template>
  <div id="SingleLedControl">
    <button @click='toggle()'>On/Off</button>
    <span v-show='status'>LED on</span>
    <span v-show='!status'>LED off</span>

    <range-slider
      class="slider"
      min="0"
      max="100"
      step="1"
      v-model="brightnessSliderVal">
    </range-slider>

    <div id="hsv">
      <h2>Here should be the HSV slider</h2>
      <slider-picker v-model="colors" @input="set_color"></slider-picker>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import RangeSlider from 'vue-range-slider';
import 'vue-range-slider/dist/vue-range-slider.css';
import slider from 'vue-color'


export default {
  name: 'SingleLedControl',
  components: {
    RangeSlider,
    'slider-picker': slider,
  },
  props: ['name'],

  data: function() {
    return {
        status: false,
        brightnessSliderVal: 50,
        colors: {h: 233, s: 100, v: 100}
    }
  },
  methods: {
    toggle: function() {
      this.status = !this.status;
      this.switch_led(this.status);
    },
    switch_led: function(state) {
      const path = 'http://192.168.0.78:5000/devices/' + this.name;
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
      const data_bright = {'r': 2.55 * val, 'g': 0, 'b': 0};
      const path = 'http://192.168.0.78:5000/devices/' + this.name
      // send put request to backend
      axios.put(path, data_bright);
    },

    set_color (colors) {
      this.colors = colors;
      // TODO send RGB color to backend
    }

  },
  watch: {
    brightnessSliderVal: function(val) {
      this.set_led_brightness(val);
    }
  }

}
</script>

<style scoped>

</style>