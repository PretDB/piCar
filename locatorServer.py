import command
import multiprocessing as mp
import os
import time
from flask import Flask, request


class server(mp.Process):
    def __init__(self, isDebug, setCalib):
        mp.Process.__init__(self)
        self.app = Flask('locator')
        self.isDebug = isDebug
        self.setCalib = setCalib
        pass

    def run(self):
        @self.app.route('/calib/', methods=['GET'])
        def startCalib():
            self.setCalib.value = 1
            while self.setCalib.value is not 0:
                time.sleep(0.1)
            print('calib done')
            return 'DONE'

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

        self.app.run(host='0.0.0.0', port=6688)
        pass
