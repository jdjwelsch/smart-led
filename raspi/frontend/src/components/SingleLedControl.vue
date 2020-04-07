<template>
    <div id="SingleLedControl">
        <button @click='toggle()'>{{button_state}}</button>

        <div id="ChromePicker">
            <chrome-picker class='picker' v-model="colors" :style="{width:'400px'}"></chrome-picker>
        </div>

    </div>
</template>

<script>
    import axios from 'axios';
    import {Chrome} from 'vue-color';


    export default {
        name: 'SingleLedControl',
        components: {
            'chrome-picker': Chrome,

        },
        props: ['name'],

        data: function () {
            return {
                power: false,
                button_state: 'LED on',
                brightnessSliderVal: 50,
                colors: {
                    hex: '#194d33',
                    hsl: {h: 150, s: 0.5, l: 0.2, a: 1},
                    hsv: {h: 150, s: 0.66, v: 0.30, a: 1},
                    rgba: {r: 25, g: 77, b: 51, a: 1},
                    a: 1
                }
            }
        },
        methods:
            {
                toggle: function () {
                    this.power = !this.power;
                    this.switch_led(this.power);

                    if (this.power) {
                        this.button_state = 'LED off'
                    } else {
                        this.button_state = 'LED on'
                    }
                }
                ,

                switch_led: function (state) {
                    const path = 'http://192.168.0.78:5000/devices/' + this.name;
                    const rgb_off = {'r': 0, 'g': 0, 'b': 0};

                    if (state) {
                        axios.put(path, {
                            'r': this.colors.rgba.r,
                            'g': this.colors.rgba.g,
                            'b': this.colors.rgba.b,
                        });
                        console.log({
                            'r': this.colors.rgba.r,
                            'g': this.colors.rgba.g,
                            'b': this.colors.rgba.b,
                        });
                    }

                    if (!state) {
                        axios.put(path, rgb_off);
                    }
                }
                ,

                set_color() {
                    const path = 'http://192.168.0.78:5000/devices/' + this.name
                    const rgb = {
                        'r': this.colors.rgba.r,
                        'g': this.colors.rgba.g,
                        'b': this.colors.rgba.b,
                    };
                    axios.put(path, rgb);

                },
            },

        watch: {
            colors() {
                this.set_color()
                if (this.colors.hsl.l > 0) {
                    this.power = true;
                }

            },
        },

        created() {
            console.log(Chrome);
            console.log(this.colors);
        }

    }
</script>
<style scoped>
    button {
        width: 50%;
        height: 40px;
    }


    div {
        margin: auto;
    }
</style>