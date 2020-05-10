<template>
    <div id="SingleLedControl">
        <H2>{{name}}</H2>
        <switches v-model="power" type-bold="true" theme="bulma"
                  label="off / on" size="lg"></switches>

        <color-picker :hue="hue"
                      :saturation="saturation"
                      :luminosity="luminosity"
                      @input="onColorInput">
        </color-picker>
        <br>

        <label for="saturation">Saturation: {{saturation}}</label><br>
        <input id='saturation' type="range" min="0" max="100"
               v-model="saturation"><br>

        <label for="luminosity">Luminosity: {{luminosity}}</label><br>
        <input id='luminosity' type="range" min="0" max="100"
               v-model="luminosity">
        <hr>
    </div>
</template>

<script>
    import axios from 'axios';
    import Switches from 'vue-switches';
    import ColorPicker from '@radial-color-picker/vue-color-picker';
    import convert from 'color-convert';

    export default {
        name: 'SingleLedControl',
        components: {
            'switches': Switches,
            ColorPicker
        },
        props: ['name', 'ServerIp', 'rgb', 'power'],

        data: function () {
            return {
                hue: 100,
                saturation: 100,
                luminosity: 50,
                device_path: 'http://' +
                    this.ServerIp +
                    ':4999/devices/' +
                    this.name,
                last_request_send: Date.now()
            }
        },
        methods:
            {
                switch_led: function () {
                    axios.put(this.device_path, this.calc_state_dict());
                    console.log('sending', this.calc_state_dict());
                }
                ,


                set_device_color() {
                    let now = Date.now();
                    // only send if there has not been an update in last 100 ms
                    if (now - this.last_request_send > 100) {
                        axios.put(this.device_path, this.calc_state_dict());
                        console.log('sending', this.calc_state_dict());
                        this.last_request_send = now;
                    }
                },
                // calculate rgb state dict for sending to backend
                calc_state_dict() {
                    let rgb_vals = convert.hsl.rgb(
                        this.hue,
                        this.saturation,
                        this.luminosity)
                    return {'rgb': rgb_vals, 'power': this.power}
                },

                set_hsl_values_from_rgb() {
                    this.hue = convert.rgb.hsl(this.rgb)[0];
                    this.saturation = convert.rgb.hsl(this.rgb)[1];
                    this.luminosity = convert.rgb.hsl(this.rgb)[2];
                },

                onColorInput(hue) {
                    this.hue = hue;
                },
            },

        watch: {
            power() {
                this.switch_led()
            },

            // update internal hsl values when rgb is changed
            // (i. e. by broadcast from backend)
            rgb() {
                this.set_hsl_values_from_rgb()
            },

            // send set_color request when hsl values are changed
            luminosity() {
                this.set_device_color();
            },
            hue() {
                this.set_device_color();
            },
            saturation() {
                this.set_device_color();
            }
        },

        created() {
            this.set_hsl_values_from_rgb()
        }
    }
</script>

<style scoped>
    @import '~@radial-color-picker/\
            vue-color-picker/dist/vue-color-picker.min.css';

    /*
    css styling for the range slider was inspired by
    http://danielstern.ca/range.css/#/
     */

    input[type=range] {
        -webkit-appearance: none;
        margin: 18px 0;
        width: 90%;
    }

    input[type=range]:focus {
        outline: none;
    }

    input[type=range]::-webkit-slider-runnable-track {
        width: 96%;
        height: 8.4px;
        cursor: pointer;
        animate: 0.2s;
        background: #3071a9;
        border-radius: 1.3px;
        border: 0.2px solid #010101;
    }

    input[type=range]::-webkit-slider-thumb {
        border: 1px solid #000000;
        height: 36px;
        width: 16px;
        border-radius: 3px;
        background: #ffffff;
        cursor: pointer;
        -webkit-appearance: none;
        margin-top: -14px;
    }

    input[type=range]:focus::-webkit-slider-runnable-track {
        background: #367ebd;
    }

    input[type=range]::-moz-range-track {
        width: 96%;
        height: 8.4px;
        cursor: pointer;
        animate: 0.2s;
        background: #3071a9;
        border-radius: 1.3px;
        border: 0.2px solid #010101;
    }

    input[type=range]::-moz-range-thumb {
        border: 1px solid #000000;
        height: 36px;
        width: 16px;
        border-radius: 3px;
        background: #ffffff;
        cursor: pointer;
    }

    input[type=range]::-ms-track {
        width: 100%;
        height: 8.4px;
        cursor: pointer;
        animate: 0.2s;
        background: transparent;
        border-color: transparent;
        border-width: 16px 0;
        color: transparent;
    }

    input[type=range]::-ms-fill-lower {
        background: #2a6495;
        border: 0.2px solid #010101;
        border-radius: 2.6px;
    }

    input[type=range]::-ms-fill-upper {
        background: #3071a9;
        border: 0.2px solid #010101;
        border-radius: 2.6px;
    }

    input[type=range]::-ms-thumb {
        border: 1px solid #000000;
        height: 36px;
        width: 16px;
        border-radius: 3px;
        background: #ffffff;
        cursor: pointer;
    }

    input[type=range]:focus::-ms-fill-lower {
        background: #3071a9;
    }

    input[type=range]:focus::-ms-fill-upper {
        background: #367ebd;
    }

    div {
        margin: auto auto 1cm;
    }
</style>