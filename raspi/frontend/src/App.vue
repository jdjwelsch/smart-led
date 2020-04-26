<template>
    <div id="app">
        <VerticalSingleLedControl
            v-for="(initialData, i) in state"
            :name="initialData.name"
            :ref="initialData.name"
            :server-ip="server_ip"
            :rgb="initialData.rgb"
            :key="i"
        />
    </div>
</template>

<script>

    import 'vue-range-slider/dist/vue-range-slider.css'
    import VerticalSingleLedControl from "./components/VerticalSingleLedControl";

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
