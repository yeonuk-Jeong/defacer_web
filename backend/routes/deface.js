var express = require('express');
var router = express.Router();

const uuid = require('uuid');
const fs = require('fs');
const path = require("path");
const io = require("socket.io-client");

var multer = require('multer');
var config = require('../config/config.json');

let uniqueDir = '';
let todayFolder = '';

Date.prototype.yyyymmdd = function() {
  var mm = this.getMonth() + 1; // getMonth() is zero-based
  var dd = this.getDate();

  return [this.getFullYear(),
          (mm>9 ? '' : '0') + mm,
          (dd>9 ? '' : '0') + dd
         ].join('');
};

let storage = multer.diskStorage({
    destination: function(req, file ,callback){
      if(req.files.length === 1){
        let today = new Date();
        todayFolder = today.yyyymmdd();
        uniqueDir = uuid.v4();
      }
      const filePath = path.join(path.join(config.path.download, todayFolder), uniqueDir)+path.sep;
      if(!fs.existsSync(filePath)){
        fs.mkdirSync(filePath, { recursive: true });
      }
      callback(null, filePath)
    },
    filename: function(req, file, callback){
      let extension = path.extname(file.originalname);
      let basename = path.basename(file.originalname, extension);
      callback(null, basename + extension);
    }
});

// 1. 미들웨어 등록
let upload = multer({
    storage: storage
});

/* Request files defacing */
router.post('/', upload.array('files'), async function(req, res, next) {
  if(!req.files || !req.files[0].destination || !req.body.type || !req.body.prefix || !req.body.parts){
    console.log(req.files + ' ' + req.files.destination + ' ' + req.body.type + ' ' + req.body.prefix + ' ' + req.body.parts);
    res.status(409).json({status: false, 'msg': 'There is no necessary key and value you sent. Please, check the request body out again.'});
  }

  folderPath = path.resolve( req.files[0].destination );
  filePath = path.resolve( req.files[0].path );
  
  //connect socket by requests
  var socket = io.connect('http://localhost:3100');
  socket.on('connect', function() {
    socket.emit('login', { name: 'api-server' });
  });

  socket.emit('request', {folderPath : folderPath, filePath: filePath, type: req.body.type, parts: req.body.parts, prefix: req.body.prefix});
  await socket.on('response', async function(data){
    if(data['state']){
      res.status(200).json({status: true, 'filePath': data['filePath'], 'files': data['files'], 'download': data['download']});
    }else{
      res.status(409).json({status: false, 'msg': data['msg']});
    }
    socket.close();
  });
  
});

router.get('/workers', async function(req, res, next) {
  //connect socket by requests
  var socket = io.connect('http://localhost:3100');
  socket.on('connect', function() {
    socket.emit('login', { name: 'api-server' });
  });
  
  socket.emit('getWorkers', "");
  await socket.on("workers", async function(data){
    if(data['state']){
      res.status(200).json({status: true, 'total': data['total'], 'idle': data['idle'], 'running': data['running']});
    }else{
      res.status(409).json({status: false, 'msg': data['msg']});
    }
    socket.close();
  });
  
});

module.exports = router;
