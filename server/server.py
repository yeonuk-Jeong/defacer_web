import eventlet
import socketio
import time
import threading

sio = socketio.Server()
app = socketio.WSGIApp(sio)

clients = []

# This is for managing defacer clients
class Client:
    def __init__(self, name, sid):
        self.name = name
        self.sid = sid
        self.state = True

    def setState(self, state):
        self.state = state


@sio.on('login')
def onLogin(sid, data):
    idx = 0
    # manage sockets without comming from backend.
    print(data['name'])
    if data['name'] != "api-server" :
        idx = len(clients)
        clients.append(Client(data['name'], sid))
        print('new client connected : '+sid)


@sio.on('request')
def requestMessage(sid, data):
    # request for defacing files
    print("Received new requests")
    cnt = 0
    worker = findIdleWorker()
    while not worker:
        time.sleep(1)
        worker = findIdleWorker()
        cnt += 1
        if cnt == 5:
            sio.emit('response', {'state': False, 'msg': "Failed to find idle worker. Please try it again."}, room=sid)
            return

    sio.emit('worker', {'filePath': data['filePath'], 'folderPath': data['folderPath'], 'type': data['type'], 'parts': data['parts'], 'prefix': data['prefix'],'sid': sid}, room=worker)

def findIdleWorker():
    for idx, client in enumerate(clients):
        if client.state == True:
            client.setState(False)
            return client.sid

    print("Couldn't find idle worker.");
    return False

def setWorkerIdle(sid):
    for idx, client in enumerate(clients):
        if client.sid == sid:
            client.setState(True)

@sio.on('response')
def responseMessage(sid, data):
    print('response from ' + sid)
    ret = setWorkerIdle(sid)
    if data['state'] == True:
        sio.emit('response', {'state': True, 'filePath': data['filePath'], 'files': data['files'], 'download': data['download']}, room=data['sid'])
    else:
        sio.emit('response', {'state': False, 'msg': data['msg']}, room=data['sid'])

@sio.on('getWorkers')
def getWorkersInfo(sid, data):
    idle = 0
    total = len(clients)
    for idx, client in enumerate(clients):
        if client.state == True:
            idle += 1
    run = total - idle
    sio.emit('workers', {'state': True, 'total': total, 'idle': idle, 'running': run})

@sio.event()
def messageToDefacer(sid, data):
    sio.emit('worker', {'msg': data})
    print('message ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    for idx, client in enumerate(clients):
        if client.sid == sid:
            clients.pop(idx)
    
    print(len(clients))

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 3100)), app)