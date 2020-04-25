<template>
    <div id="app">
        <!-- <H2>LED Jona</H2>
        <VerticalSingleLedControl name="led1" :server-ip="server_ip"></VerticalSingleLedControl>

        <H2>LED Kueche</H2>
        <VerticalSingleLedControl name="led2" :server-ip="server_ip"></VerticalSingleLedControl> -->

        <VerticalSingleLedControl
            v-for="(initialData, i) in state"
            :name="initialData.name"
            :server-ip="server_ip"
            :initialData="initialData.state"
            :key="i"
        />
    </div>
</template>

<script>

    import 'vue-range-slider/dist/vue-range-slider.css'
    // import SingleLedControl from "./components/SingleLedControl";
    import VerticalSingleLedControl from "./components/VerticalSingleLedControl";

    // TODO: get devices from backend
    // TODO: construct controls for each device
    // TODO: establish socket communication

    export default {
        name: 'App',
        components: {
            VerticalSingleLedControl,
        },
        data: function () {
            return {
                server_ip: '192.168.0.78',
                isConnected: false,
                socketMessage: '',
                state: [],
            }
        },
        sockets: {
            connect() {
                this.isConnected = true;
                console.log('socket connected')
            },
            disconnect() {
                this.isConnected = false;
            },
            stateUpdate(state) {
                this.state = state
                console.log(this.state)
            }
        },
        mounted() {
            this.$socket.emit('getState')
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
