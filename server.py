import command
import current_cmd
import multiprocessing as mp
from flask import Flask, request

class server(mp.Process):
    def __init__(self, cmd, fire, speed):
        self.app = Flask('controller')
        self.cmd = cmd
        self.speed = speed
        self.fire = fire
        pass

    def run(self):
        @self.app.route('/controller', methods=['POST', 'GET'])
        def controller():
            if request.method == 'POST':
                incomming = request.get_json()
                SetCommand(incomming)
                return str(current_cmd.com) + ', ' + str(current_cmd.args)
            elif request.method == 'GET':
                return str(current_cmd.com) + ', ' + str(current_cmd.args)

        def SetCommand(inCommingJson):
            if inCommingJson['Type'] == 'instruction':
                if inCommingJson['FromRole'] == 'Controller':
                    self.com.value = int(inCommingJson['Command'])
                    self.speed.value = float(inCommingJson['Args']['Speed'])
                    self.fire.value = int(inCommingJson['Args']['Speed'])
                    print('com: ', command.Command(self.com.value), '\tspeed: ', self.speed.value, '\tfire: ', bool(self.fire.value))
            pass
        self.app.run(host='0.0.0.0', port=6688)

        pass

app = Flask(__name__)

# The server set the command and something else
@app.route('/controller', methods=['POST', 'GET'])
def controller():
    if request.method == 'POST':
        incomming = request.get_json()
        SetCommand(incomming)
        return str(current_cmd.com) + ', ' + str(current_cmd.args)
    elif request.method == 'GET':
        return str(current_cmd.com) + ', ' + str(current_cmd.args)

def SetCommand(inCommingJson):
    if inCommingJson['Type'] == 'instruction':
        if inCommingJson['FromRole'] == 'Controller':
            current_cmd.com = command.Command(int(inCommingJson['Command']))
            current_cmd.args = inCommingJson['Args']
            print(current_cmd.com)
    pass
