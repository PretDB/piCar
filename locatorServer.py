import command
import multiprocessing as mp
import os
import time
import cv2
from flask import Flask, request, Response, render_template


class server(mp.Process):
    def __init__(self, isDebug, setCalib, buffNum):
        mp.Process.__init__(self)
        self.app = Flask('locator')
        self.isDebug = isDebug
        self.setCalib = setCalib
        self.buffNum = buffNum
        pass

    def run(self):
        def stream():
            while True:
                if self.buffNum.value == 1:
                    img = open('/var/locator/1.jpg', 'rb').read()
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
                elif self.buffNum.value == 2:
                    img = open('/var/locator/2.jpg', 'rb').read()
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
                else:
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')
                pass
            pass
        @self.app.route('/stream_simple.html')
        def stream_simple():
            return render_template('stream_simple.html')
        @self.app.route('/calib/', methods=['GET'])
        def startCalib():
            self.setCalib.value = 1
            while self.setCalib.value is not 0:
                time.sleep(0.1)
            print('calib done')
            return 'DONE'

        @self.app.route('/streamer')
        def streamer():
            return Response(stream(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
            pass
        @self.app.route('/locator', methods=['POST', 'GET'])
        def controller():
            if request.method == 'POST':
                incomming = request.get_json()
                SetCommand(incomming)
                return 'com: ' + str(command.Command(self.com.value)) + '\tspeed: ' + str(self.speed.value) + '\tfire: ' + str(bool(self.fire.value))
            elif request.method == 'GET':
                return 'com: ' + str(command.Command(self.com.value)) + '\tspeed: ' + str(self.speed.value) + '\tfire: ' + str(bool(self.fire.value))

        def SetCommand(inCommingJson):
            if inCommingJson['Type'] == 'instruction':
                if inCommingJson['FromRole'] == 'Controller':
                    self.isDebug.value = int(inCommingJson['Args']['Debug'])
                    print('isDebug: ', bool(self.isDebug.value))
            pass

        self.app.run(host='0.0.0.0', port=8080)
        pass
