#!/usr/bin/python3

import re
import signal
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import cv2
import subprocess

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
from multiprocessing.connection import Listener
from time import sleep

DBusGMainLoop(set_as_default=True)
Gst.init(None)

loop = GLib.MainLoop()

bus = dbus.SessionBus()
request_iface = 'org.freedesktop.portal.Request'
screen_cast_iface = 'org.freedesktop.portal.ScreenCast'

pipeline = None

desired_light = 1500  # 1 to 65025

portal = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')

def terminate():
    if pipeline is not None:
        pipeline.set_state(Gst.State.NULL)
    loop.quit()

request_token_counter = 0
session_token_counter = 0
sender_name = re.sub(r'\.', r'_', bus.get_unique_name()[1:])

def new_request_path():
    global request_token_counter
    request_token_counter = request_token_counter + 1
    token = 'u%d' % request_token_counter
    path = '/org/freedesktop/portal/desktop/request/%s/%s' % (sender_name, token)
    return (path, token)

def new_session_path():
    global session_token_counter
    session_token_counter = session_token_counter + 1
    token = 'u%d' % session_token_counter
    path = '/org/freedesktop/portal/desktop/session/%s/%s' % (sender_name, token)
    return (path, token)

def screen_cast_call(method, callback, *args, options={}):
    (request_path, request_token) = new_request_path()
    bus.add_signal_receiver(callback,
                            'Response',
                            request_iface,
                            'org.freedesktop.portal.Desktop',
                            request_path)
    options['handle_token'] = request_token
    method(*(args + (options,)),
           dbus_interface=screen_cast_iface)

def on_gst_message(bus, message):
    type = message.type
    if type == Gst.MessageType.EOS or type == Gst.MessageType.ERROR:
        terminate()

def play_pipewire_stream(node_id):

    margin = 10
    target = 100
    checkcnt = 0
    checkpoint = 1
    maxcheckpoint = 100
    immersive_multiplier = 1.8
    offset = 0
    mode = 'disabled'
    running = True

    listener = Listener(address=("localhost", 21827))
    blistener = Listener(address=("localhost", 21828))

    empty_dict = dbus.Dictionary(signature="sv")
    portal = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
    fd_object = portal.OpenPipeWireRemote(session, empty_dict, dbus_interface=screen_cast_iface)
    fd = fd_object.take()
    pipeline_string = 'pipewiresrc fd=%d path=%u ! videoconvert ! appsink sync=false'
    badpipeline_string = 'pipewiresrc fd=%d path=%u ! videoconvert ! framerate=60/1 ! appsink sync=false'

    # Create a VideoCapture object with GStreamer pipeline
    cap = cv2.VideoCapture(pipeline_string % (fd, node_id), cv2.CAP_GSTREAMER)

    # Check if the VideoCapture object was successfully opened
    if not cap.isOpened():
        print('Failed to open pipeline.')
        exit(1)

    # Read and display frames from the pipeline
    conn = listener.accept()
    connb = blistener.accept()
    backlight = int(subprocess.check_output("light -r", shell=True))
    while running:
        while conn.poll():
            msg = conn.recv()

            if msg == "EXIT":
                running = False
            elif msg[0] == "margin":
                margin = int(msg[1])
            elif msg[0] == "target":
                target = int(msg[1])
            elif msg[0] == "mode":
                mode = str(msg[1])
            elif msg[0] == "offset":
                offset = int(msg[1])
            elif msg[0] == "multiplier":
                immersive_multiplier = float(msg[1])
        if mode != "disabled":
            while connb.poll():
                msg = connb.recv()
                if msg == "value":
                    connb.send(backlight)
            ret, frame = cap.read()

            if not ret:
                print('=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                break

            # Calculate the overall image of the grayscale frame
            image = float(cv2.cvtColor(cv2.resize(frame, (200, 200)), cv2.COLOR_BGR2GRAY).mean())
            if checkcnt >= checkpoint:
                checkcnt = 0
                buff = int(subprocess.check_output("light -r", shell=True))
                if buff == backlight:
                    if checkpoint != maxcheckpoint:
                        checkpoint = maxcheckpoint
                    else:
                        pass
                else:
                    checkpoint = 1
                    print('something is wrong, backlight is: ' + str(buff) + ' instead of ' + str(backlight) + ', trying to set again')
                    backlight = buff

            if mode == 'normal':
                if int(image) <= 1:
                    if backlight == 0:
                        pass
                    else:
                        subprocess.call(('light', '-S', '-r', str(0)))
                        backlight = 0

                elif abs((backlight * image) // 255 - target) > margin:
                    val = int((target / image) * 255)
                    if val > 255:
                        subprocess.call(('light', '-S', '-r', '255'))
                        backlight = 255
                    else:
                        subprocess.call(('light', '-S', '-r', str(val)))
                        backlight = val

            elif mode == 'immersive':
                if int(image * immersive_multiplier) + offset > 255:
                    subprocess.call(('light', '-S', '-r', str(255)))
                    backlight = 255
                else:
                    backlight = int(image * immersive_multiplier + offset)
                    subprocess.call(('light', '-S', '-r', str(backlight)))

            checkcnt += 1
        else:
            sleep(0.5)

    # Release the VideoCapture object and close windows
    cap.release()
    cv2.destroyAllWindows()


def on_start_response(response, results):
    if response != 0:
        print("Failed to start: %s" % response)
        terminate()
        return

    print("streams:")
    for (node_id, stream_properties) in results['streams']:
        print("stream {}".format(node_id))
        play_pipewire_stream(node_id)

def on_select_sources_response(response, results):
    portal = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
    if response != 0:
        print("Failed to select sources: %d" % response)
        terminate()
        return

    print("sources selected")
    global session
    screen_cast_call(portal.Start, on_start_response,
                     session, '')

def on_create_session_response(response, results):
    portal = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
    if response != 0:
        print("Failed to create session: %d" % response)
        terminate()
        return

    global session
    session = results['session_handle']
    print("session %s created" % session)

    screen_cast_call(portal.SelectSources, on_select_sources_response,
                     session,
                     options={'multiple': False,
                              'types': dbus.UInt32(1 | 2)})

(session_path, session_token) = new_session_path()
screen_cast_call(portal.CreateSession, on_create_session_response,
                 options={'session_handle_token': session_token})

try:
    loop.run()
except KeyboardInterrupt:
    terminate()
