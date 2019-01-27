import command
import current_cmd
from flask import Flask, request

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
