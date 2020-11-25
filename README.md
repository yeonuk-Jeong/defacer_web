# defacer_web

  
### 로컬 이외에서 접속하려면,
frontend/src/views/OriginDwv.vue에서   
var response = await axios.post('http://localhost:3000/api/deface', formData, {  
부분의 localhost를 서버 주소로 바꿈.  

1. frontend 폴더에서 npm install, npm start로 실행

  
2. backend/config 폴더 아래에 json 파일에서 다운로드 경로 설정 해줌. 지금은 D://
backend폴더로 가서 npm install
npm start


pip install eventlet  
pip install python-soketio  
3. server 폴더에서 python server.py로 소켓서버 실행  
  
  
4. client 폴더에서 python client.py로 딥러닝 모델 실행시킴  
  
4가지 모두 실행시켜놓고 나서 프론트엔드에 주소로 들어가면, (서버주소:8080)  
choose file 버튼을 눌러서 .dcm 파일을 업로드한다. 예전에 드린 예시 다이콤 파일인 S63516 폴더 안의 모든 파일을 선택해야함  
start defacing 누름  




