from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# TODO: replace dict with SQLite database
global devices_dict
devices_dict = {}


@app.route('/devices', methods=['GET', 'POST'])
def register_device():

    if request.method == 'POST':
        name = request.json['name']
        ip = request.json['ip']

        if name in devices_dict:
            msg = {'message': 'device already exists'}
            return jsonify(msg)
        else:
            devices_dict.update({name: {'ip': ip, 'r': 0, 'g': 0, 'b': 0}})
            return Response("{'message': 'device created'}", status=201, mimetype='application/json')

    if request.method == 'GET':
        return jsonify(devices_dict)


@app.route('/devices/<name>', methods=['GET', 'PUT'])
def device_status(name):
    if request.method == 'GET':
        return jsonify(devices_dict[name])

    if request.method == 'PUT':
        status_dict = {}
        for color in ['r', 'g', 'b']:
            if color in request.json:
                color_value = request.json[color]
                status_dict.update({color: color_value})
        devices_dict[name].update(status_dict)

        set_device_status(name, status_dict)

        return Response("{'message': 'status changed'}", status=201, mimetype='application/json')


def set_device_status(device_name, status_dict):
    ip = devices_dict[device_name]['ip']
    url = 'http://' + ip + ':80/leds'
    print(f'send {status_dict} to {url}')
    requests.put(url, json=status_dict)


@app.route('/')
def hello_world():
    return 'Welcome to LED control'

# TODO add basic buttons for wifi controller


if __name__ == '__main__':
    app.run()
