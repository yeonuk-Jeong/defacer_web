import os
import zipfile
import socketio
import uuid
from model.defacer import Defacer
import time

uuid = uuid.uuid1()
sio = socketio.Client()
df = Defacer()
baseURL = "http://localhost:3000/download/"

@sio.event
def connect():
    # connect to server
    print('connect to server')
    sio.emit('login', {'name': uuid.hex})

@sio.on('worker')
def worker(data):
    # data object has sid, filePath keys.
    responseData = data['parts'].split(',')
    map_object = map(int, responseData)
    parts = list(map_object)

    folderName = os.path.basename(data['folderPath'])
    dateName =os.path.basename(os.path.dirname(data['folderPath']))
    fileName = os.path.basename(data['filePath'])
    destPath = os.path.join(data['folderPath'], "dest")
    verifPath = os.path.join(destPath, "verification")
    zipPath = os.path.join(data['folderPath'], "result.zip")
    url = baseURL+dateName + "/" + folderName+"/"
    downloadUrl = url+'result.zip'
    destUrl = url+'dest/'

    print('folderName : '+ folderName)
    print('fileName : '+ fileName)
    print('destPath : '+ destPath)
    print('verifPath : '+ verifPath)
    print('zipPath : '+ zipPath)
    print('baseUrl : '+ url)

    if data['type'] == 'dicom':
        inputData = data['folderPath']
        if not os.path.isdir(destPath):
            os.makedirs(destPath)
        result = df.Deidentification_image_dcm(parts, inputData, destPath, verifPath, destUrl, "did")
    else:
        inputData = data['filePath']
        if not os.path.isdir(destPath):
            os.makedirs(destPath)
        result = df.Deidentification_image_nii(parts, inputData, destPath, verifPath, destUrl, "did")

    # Abstract all the result files
    resultZip = zipfile.ZipFile(zipPath, 'w')
    if result['success']:
        for folder, subfolders, files in os.walk(destPath): 
            for file in files:
                resultZip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), destPath), compress_type = zipfile.ZIP_DEFLATED)
 
        resultZip.close()
        sio.emit('response', {'state': True, 'filePath': result['path'], 'files': result['files'], 'download': downloadUrl, 'sid': data['sid']})
    else:
        sio.emit('response', {'state': False,'msg': result['msg'], 'sid': data['sid']})

@sio.event
def disconnect():
    print('disconnected from server')

if __name__ == "__main__" :
    sio.connect('http://localhost:3100')

    sio.wait()