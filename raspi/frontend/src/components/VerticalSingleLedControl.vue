<template>
    <div id="SingleLedControl">
        <H2>{{name}}</H2>
        <switches v-model="power" type-bold="true" theme="bulma"
                  label="off / on" size="lg"></switches>

        <color-picker :hue="hue"
                      :saturation="saturation"
                      :luminosity="luminosity"
                      @input="onColorInput">
        </color-picker><br>

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
        props: ['name', 'ServerIp', 'rgb'],

        data: function () {
            return {
                power: false,
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
            switch_led: function (state) {
                const rgb_off = {'rgb': [0, 0, 0]};

                if (state) {
                    const rgb_dict = this.calc_rgb_dict()
                    axios.put(this.device_path, rgb_dict);
                    console.log(this.device_path);
                    console.log(rgb_dict);
                }

                if (!state) {
                    axios.put(this.device_path, rgb_off);
                }
            }
            ,

            set_device_color() {
                let now = Date.now();
                // only send if there has not been an update in the last 500 ms
                if (now - this.last_request_send > 500) {
                        axios.put(this.device_path, this.calc_rgb_dict());
                        console.log('sending', this.calc_rgb_dict());
                        this.last_request_send = now;
                }
            },
            calc_rgb_dict() {
                let rgb_vals = convert.hsl.rgb(
                    this.hue,
                    this.saturation,
                    this.luminosity)
                return {'rgb': rgb_vals}
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
                this.switch_led(this.power)
            },

            // update internal hsl values when rgb is changed
            // (i. e. by broadcast)
            rgb() {
                this.set_hsl_values_from_rgb()
            },

            // send set_color request when hsl values are changed

            luminosity() {
                this.power = this.luminosity > 0;
                this.set_device_color();
            },
            hue() {
                this.power = this.luminosity > 0;
                this.set_device_color();
            },
            saturation() {
                this.power = this.luminosity > 0;
                this.set_device_color();
            }
        }
        ,

        computed: {}
        ,
        created() {
            this.set_hsl_values_from_rgb()
        }
    }
</script>
<style scoped>
    @import '~@radial-color-picker/vue-color-picker/dist/vue-color-picker.min.css';

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
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
        background: #3071a9;
        border-radius: 1.3px;
        border: 0.2px solid #010101;
    }

    input[type=range]::-webkit-slider-thumb {
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
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
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
        background: #3071a9;
        border-radius: 1.3px;
        border: 0.2px solid #010101;
    }

    input[type=range]::-moz-range-thumb {
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
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
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
    }

    input[type=range]::-ms-fill-upper {
        background: #3071a9;
        border: 0.2px solid #010101;
        border-radius: 2.6px;
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
    }

    input[type=range]::-ms-thumb {
        /*box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;*/
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
        margin: auto;
        margin-bottom: 1cm;
    }
</style>