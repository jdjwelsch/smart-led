<template>
    <div id="SingleLedControl">
        <button @click='toggle()'>On/Off</button>
        <span v-show='power'>LED on</span>
        <span v-show='!power'>LED off</span>

        <range-slider
                class="slider"
                min="0"
                max="100"
                step="1"
                v-model="brightnessSliderVal">
        </range-slider>

        <div id="hsv">
            <h2>Here should be the HSV slider</h2>
            <slider-picker v-model="hslColor"></slider-picker>
        </div>

    </div>
</template>

<script>
    import axios from 'axios';
    import RangeSlider from 'vue-range-slider';
    import 'vue-range-slider/dist/vue-range-slider.css';
    import {Slider} from 'vue-color';


    export default {
        name: 'SingleLedControl',
        components: {
            RangeSlider,
            'slider-picker': Slider,
        },
        props: ['name'],

        data: function () {
            return {
                power: false,
                brightnessSliderVal: 50,
                hslColor: {r: 127, g: 100, b: 0.5}
            }
        },
        methods: {
            toggle: function () {
                this.power = !this.power;
                this.switch_led(this.power);
            },

            switch_led: function (state) {
                const path = 'http://192.168.0.78:5000/devices/' + this.name;
                const rgb_off = {'r': 0, 'g': 0, 'b': 0};

                if (state) {
                    axios.put(path, {'r': this.hslColor.rgba.r, 'g': this.hslColor.rgba.g, 'b': this.hslColor.rgba.b});
                    console.log({'r': this.hslColor.rgba.r, 'g': this.hslColor.rgba.g, 'b': this.hslColor.rgba.b});
                }

                if (!state) {
                    axios.put(path, rgb_off);
                }
            },

            set_led_brightness: function (val) {
                this.hslColor.hsl.l = val / 100;
                console.log(this.hslColor)
                const path = 'http://192.168.0.78:5000/devices/' + this.name
                const rgb = {'r': this.hslColor.rgba.r, 'g': this.hslColor.rgba.g, 'b': this.hslColor.rgba.b};
                axios.put(path, rgb);

            },

            set_color() {
                // TODO send RGB color to backend
                const path = 'http://192.168.0.78:5000/devices/' + this.name
                const rgb = {'r': this.hslColor.rgba.r, 'g': this.hslColor.rgba.g, 'b': this.hslColor.rgba.b};
                axios.put(path, rgb);

            },
        },

        watch: {
            brightnessSliderVal() {
                this.set_led_brightness();
            },


            hslColor(hslColor) {
                //hsv2rgb()
                console.log(hslColor.rgba.r);
                console.log(hslColor.rgba.g);
                console.log(hslColor.rgba.b);
                this.set_color();

                if (hslColor.hsl.l > 0){
                    this.power = true;
                }

            }

        },

        created() {
            console.log(Slider)
            console.log(this.hslColor)
        }

    }
</script>

<style scoped>

</style>