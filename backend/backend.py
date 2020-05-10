import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import sql_utils


log = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend/dist/')
# allow for cross origin communication, as frontend and backend run on a
# different port. As this application is not publicly accessible, there should
# be no security concerns. Watch out, if you plan to expose your application to
# the internet.
CORS(app, resources={r'/*': {'origins': '*'}})
socket = SocketIO(app, path='/ws/socket.io')
db_file = 'devices.db'
state_update_running = False


# set up HTTPAdapter to use for requests. Plain request does not allow to set
# the number of retries attempted for an http request.
# set max retries to 1, as put requests send to LEDs are send twice a
# second anyway and prevent the application from slowing down, if one client is
# unreachable.
retry_strategy = Retry(total=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


@app.before_first_request
def set_up_database():
    """
    Set up SQLite data base to store registered devices and their status.
    """
    log.debug('Database set up started')
    sql_utils.create_devices_table(db_file)


@app.route('/devices', methods=['GET', 'POST'])
def register_device():
    """
    Register new wifi-controlled devices on start up.

    New devices are expected to send a POST request with a json containing
    fields 'ip' and 'name'.
    :return:
    """
    device_list = sql_utils.get_device_list_sql(db_file)
    if request.method == 'POST':
        name = request.json['name']
        ip = request.json['ip']

        if name in device_list:
            sql_utils.update_device_ip_sql(db_file, name, ip)
            log.info('device %s already exists' % name)
            msg = {'message': 'device already exists'}
            return jsonify(msg)

        else:
            sql_utils.create_device_sql(db_file,
                                        {'name': name,
                                         'ip': ip,
                                         'rgb': (0, 0, 0),
                                         'power': 0})
            log.info('device %s registered at %s.' % (name, ip))
            return Response("{'message': 'device created'}",
                            status=201,
                            mimetype='application/json')

    if request.method == 'GET':
        return jsonify(device_list)


@app.route('/devices/<device_name>', methods=['GET', 'PUT'])
def device_status(device_name):
    """
    Endpoint for communication with frontend for setting LED strip properties.

    The GET method is only implemented as a fall back, normally LED device
    states are send to frontend via websockets.

    :param device_name: Name of device whose properties shall be accessed.
    """
    if request.method == 'GET':
        device_status = sql_utils.get_device_status_sql(db_file, device_name)[0]
        return jsonify(device_status)

    if request.method == 'PUT':
        # update server data base
        status_dict = {'rgb': request.json['rgb'],
                       'power': request.json['power']}
        sql_utils.set_device_status_sql(db_file,
                                        device_name=device_name,
                                        status_dict=status_dict)

        # start update thread
        update_leds()

        return Response("{'message': 'status changed'}",
                        status=201,
                        mimetype='application/json')


@socket.on('connect')
def client_has_connected():
    """
    Helper function for debugging.
    """
    log.info("A client has connected")


@socket.on('getState')
def send_all_devices_state():
    """
    Send state of all LED devices to frontend.

    This is used on frontend start up to set the current colors, etc.
    """
    all_device_status = sql_utils.get_device_status_sql(db_file)
    emit('stateUpdate', all_device_status)


def update_leds():
    """
    Sends the current setting to all LED devices in database every 0.5
    seconds for n_requests times.

    This is done to ensure that multiple requests to change the LED color
    coming in within a very short time span will not all be send to the
    device. Instead the database is evaluated every 0.5s, for a few times,
    which allows for a smoother color transition.
    :param n_requests: integer, how many times LED state will be updated,
    once this function was triggered.
    """
    global state_update_running

    # only start update, if there is not already an update running
    if state_update_running:
        return
    else:
        state_update_running = True
        # start update in separate thread, so that it does not block incoming
        # requests
        eventlet.spawn(_send_led_state_update)


def _send_led_state_update():
    """
    Wait for 0.5 seconds, then send a state update to all registered LED
    devices.

    This is to accommodate situations when many requests to set the LED
    color are sent to the backend within a short time span - this way the
    current state is evaluated and sent to the LED strips at maximum every
    0.5 seconds.
    """
    eventlet.sleep(0.5)
    set_device_status()

    # allow for spawning a new update thread, once finished
    global state_update_running
    state_update_running = False


def set_device_status(device_name=None):
    """
    Set state of a wifi controlled LED device.

    :param device_name: Name the device has been registered with. If None set
    device status of all devices in database
    """
    # set all devices if not specified
    if device_name is None:
        devices = sql_utils.get_device_list_sql(db_file)
    else:
        devices = [device_name]
    device_info = sql_utils.get_device_status_sql(db_file, device_name)

    # stop if there are no registered devices
    if devices is None:
        log.warning('No devices registered yet')
        return None

    # send requests to LED devices
    for i, d in enumerate(devices):
        ip = device_info[i]['ip']
        url = 'http://' + ip + ':80/leds'
        log.debug('send to %s' % url)

        # create dictionary to send to LED devices
        status_dict = {}
        for j, color in enumerate(['r', 'g', 'b']):
            status_dict.update({color: device_info[i]['rgb'][j]})
        status_dict.update({'power': device_info[i]['power']})

        # send to LED devices
        try:
            # set short timeout, so that unreachable devices don't slow down
            # the app
            http.put(url, json=status_dict, timeout=0.3)
        except requests.exceptions.ConnectionError:
            log.info('could not reach ' + url)

    # broadcast new status to all connected clients
    all_device_status = sql_utils.get_device_status_sql(db_file)
    socket.emit('stateUpdate', all_device_status, broadcast=True)


if __name__ == '__main__':
    # use this to get more informative output when debugging:
    # logging.basicConfig(level=logging.DEBUG)
    # start app
    socket.run(app, host='0.0.0.0', debug=False, port=4999)

