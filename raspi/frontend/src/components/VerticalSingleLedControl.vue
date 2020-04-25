<template>
    <div id="SingleLedControl">
        <switches v-model="power" type-bold="true" theme="bulma" label="off / on"></switches>

        <color-picker :hue="hue" :saturation="saturation" :luminosity="luminosity" @input="onColorInput"></color-picker>

        <label for="saturation">Saturation: {{saturation}}</label>
        <input id='saturation' type="range" min="0" max="100" v-model="saturation">

        <label for="luminosity">Luminosity: {{luminosity}}</label>
        <input id='luminosity' type="range" min="0" max="100" v-model="luminosity">


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
        props: ['name', 'ServerIp', 'initialData'],

        data: function () {
            return {
                power: false,
                hue: 25,
                saturation: 100,
                luminosity: 50,

                device_path: 'http://' + this.ServerIp + ':4999/devices/' + this.name,
            }
        },
        methods:
            {
                switch_led: function (state) {
                    const rgb_off = {'r': 0, 'g': 0, 'b': 0};

                    if (state) {
                        axios.put(this.device_path, {
                            'r': this.rgb[0],
                            'g': this.rgb[1],
                            'b': this.rgb[2],
                        });
                        console.log(this.device_path);
                        console.log({
                            'r': this.rgb[0],
                            'g': this.rgb[1],
                            'b': this.rgb[2],
                        });
                    }

                    if (!state) {
                        axios.put(this.device_path, rgb_off);
                    }
                }
                ,

                set_color() {
                    const rgb = {
                        'r': this.rgb[0],
                        'g': this.rgb[1],
                        'b': this.rgb[2],
                    };
                    axios.put(this.device_path, rgb);

                },

                onColorInput(hue) {
                    this.hue = hue;
                    console.log('hue (radial): ', hue);
                },

            },

        watch: {
            power() {
                this.switch_led(this.power)
            },

            rgb() {
                this.set_color();
                if (this.luminosity > 0) {
                    this.power = true;
                }
            }
        },

        computed: {
            rgb() {
                return convert.hsl.rgb(this.hue, this.saturation, this.luminosity)
            }
        },

        created() {
            // console.log(Chrome);
            // console.log(this.colors);
        }

    }
</script>
<style scoped>
    @import '~@radial-color-picker/vue-color-picker/dist/vue-color-picker.min.css';

    input[type=range] {
        -webkit-appearance: none;
        margin: 18px 0;
        width: 100%;
    }

    input[type=range]:focus {
        outline: none;
    }

    input[type=range]::-webkit-slider-runnable-track {
        width: 100%;
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
        width: 100%;
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

    button {
        width: 50%;
        height: 40px;
    }


    div {
        margin: auto;
    }
</style>