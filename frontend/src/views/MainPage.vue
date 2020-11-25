<template>
    <div>
        <v-overlay :value="overlay" style="text-align:center">
          <v-progress-circular
            :size="70"
            :width="7"
            color="purple"
            indeterminate
          ></v-progress-circular>
          <br/><br/><br/>
          <p style="color:whitesmoke;font-size:1.3em;">Processing Now. Please wait till its done.</p>
        </v-overlay>
        <br/><br/><br/><br/><br/>
        <section style="margin-bottom:50px;text-align:center">
            <h1>How to try this demo</h1><br/>
            <p>1. Download the dicom files using the button below named "Download Sample"</p>
            <p>2. Extract "sample.zip" in the specific folder. </p>
            <p>3. Click the button "Choose File" then select all the files *.dcm in that folder.(buttons will be seen by your OS language)</p>
            <p>4. Click the button "Start Defacing" below the loaded dicom image.</p>

            <br/>
            <v-btn style="background-color:#01DFA5;color:whitesmoke;margin-top:30px;" @click="downloadSample">Download Sample Files</v-btn>
            
        </section>
        <br/><br/>
        <section style="text-align:center;">
          <p style="text-align:left;margin-left:210px;color:red;">! You must choose files which have extension of ".dcm".</p>
          <form enctype="multipart/form-data" style="margin-left:15em;background-color:white;width:0.8em;">
            <input type="file" id="files" ref="files" multiple @change="previewFiles" style="font-size:1.1em;background-color:white;color:black;"/>
          </form>
        </section>
        <div class="split left">
          <section style="width:50em;height:40em;margin:10px;">
            <dwvVue ref="Original" :isLoad='this.overlay'></dwvVue>
          </section>
        </div>
        <div class="split right">
          <section style="width:50em;height:40em;margin:10px;">
            <ResultdwvVue ref="Result"></ResultdwvVue>
          </section>
        </div>
        <br/><br/>
    </div>
</template>

<script>
  import dwvVue from './OriginDwv';
  import ResultdwvVue from './ResultDwv';

  export default {
    name: 'MainPage',
    components: {
      dwvVue,
      ResultdwvVue
    },
    data: () => ({
      overlay: false,
      resultFileList: [],
      resultFile: null,
      url:'http://localhost:3000/download/sample.zip',
      resultUrl: null,
    }),
    methods: {
      onFileChange(e) {
        var files = e.target.files || e.dataTransfer.files;
        if (!files.length) return;
        this.createInput(files[0]);
      },
      createInput(file) {
        let promise = new Promise((resolve, ) => {
          var reader = new FileReader();
          var vm = this;
          reader.onload = e => {
            console.log(e);
            resolve((vm.fileinput = reader.result));
          };
          reader.readAsText(file);
        });

        promise.then(
          result => {
            /* handle a successful result */
            console.log(result);
            console.log(this.fileinput);
          },
          error => {
            /* handle an error */
            console.log(error);
          }
        );
      },
      previewFiles(event) {
        this.$refs.Original.files = event.target.files;
        //console.log(this.$refs.Original.files[0])
      },
      getOverlay: function() {
        return this.overlay;
      },
      setOverlay: function(isLoad) {
        this.overlay = isLoad;
      },
      forceFileDownload(response){
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'sample.zip') //or any other extension
        document.body.appendChild(link)
        link.click()
      },
      downloadSample: function() {
        this.$http({
          method: 'get',
          url: this.url,
          responseType: 'arraybuffer'
        })
        .then(response => {
          this.forceFileDownload(response)  
        })
        .catch(() => console.log('error occured'))
      }
    },
    watch: {
      resultFileList: function() {
        this.$refs.Result.files = this.resultFileList;
      },
      resultUrl: function() {
        this.$refs.Result.url = this.resultUrl;
      }
    }
  }
</script>
<style scoped>
h1 {
  font-size: 1.5em;
  margin-bottom: 1em;
}

p {
  font-size: 1.1em;
  margin-bottom: 1em;
  margin-left: 1em;
}
.right {
  height: 90%;
  width: 50%;
  padding-top: 20px;
  float: right;
  background-color: #212121;
  color: whitesmoke;
}

/* Control the left side */
.left {
  height: 90%;
  width: 50%;
  padding-top: 20px;
  float: left;
  background-color: #212121;
  color: whitesmoke;
}
</style>
