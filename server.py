import command
import multiprocessing as mp
from flask import Flask, request


class server(mp.Process):
    def __init__(self, cmd, fire, speed):
        mp.Process.__init__(self)
        self.app = Flask('controller')
        self.com = cmd
        self.speed = speed
        self.fire = fire
        pass

    def run(self):
        @self.app.route('/controller', methods=['POST', 'GET'])
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
                    self.com.value = int(inCommingJson['Command'])
                    self.speed.value = float(inCommingJson['Args']['Speed'])
                    self.fire.value = int(inCommingJson['Args']['Fire'])
                    print('com: ', command.Command(self.com.value), '\tspeed: ', self.speed.value, '\tfire: ', bool(self.fire.value))
            pass
        self.app.run(host='0.0.0.0', port=6688)

        pass
