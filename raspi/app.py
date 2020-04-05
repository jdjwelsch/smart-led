from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)


# TODO: replace dict with SQLite database
global devices_dict
devices_dict = {}
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/devices', methods=['GET', 'POST'])
def register_device():
    """
    Register new wifi-controlled devices on start up.

    New devices are expected to send a POST request with a json containing fields 'ip' and 'name'.
    :return:
    """
    if request.method == 'POST':
        name = request.json['name']
        ip = request.json['ip']

        if name in devices_dict:
            print(f'device {name} already exists')
            msg = {'message': 'device already exists'}
            return jsonify(msg)
        else:
            devices_dict.update({name: {'ip': ip, 'r': 0, 'g': 0, 'b': 0}})
            print(f'device {name} registered at {ip}.')
            return Response("{'message': 'device created'}", status=201, mimetype='application/json')

    if request.method == 'GET':
        return jsonify(devices_dict)


@app.route('/devices/<name>', methods=['GET', 'PUT'])
def device_status(name):
    """
    Endpoint for communication with frontend for setting device properties.
    :param name: Name of device whose properties shall be accessed.
    :return:
    """
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
    """
    Set state of a wifi controlled device.

    :param device_name: Name the device has been registered with
    :param status_dict: dictionary containing key-value pairs to be set
    :return:
    """
    ip = devices_dict[device_name]['ip']
    url = 'http://' + ip + ':80/leds'
    print(f'send {status_dict} to {url}')
    requests.put(url, json=status_dict)


@app.route('/')
def hello_world():
    return 'Welcome to LED control'

# TODO add basic buttons for wifi controller


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
