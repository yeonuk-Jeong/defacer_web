<template>
<div>
  <div id="dwv">
    <div class="layerContainer">
      <h1>Original Dicom File</h1>
      <div class="dropBox dropBoxBorder md-body-1">
          <p>Drag and drop or choose dicom data.</p>
      </div>
      <canvas class="imageLayer">Only for HTML5 compatible browsers...</canvas>
      <div class="drawDiv"></div>
    </div>
  </div>
  <div style="text-align:center;">
      <v-btn style="background-color:#01DFA5;color:whitesmoke;margin-top:30px;" @click="prev">Prev</v-btn>
      &nbsp;
      <v-btn style="background-color:#01DFA5;color:whitesmoke;margin-top:30px;" @click="next">Next</v-btn>
  </div>
  <div style="text-align:center;padding:50px;">
    <v-card fluid class="Card__container" color="light-green lighten-5">
      <v-row>
        <v-col>
          <h3>Check you want to erase</h3>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="3" md="3">
          <v-checkbox class="white--text" color="primary" v-model="eyes" label="Eyes"></v-checkbox>
        </v-col>
        <v-col cols="12" sm="3" md="3">
          <v-checkbox class="white--text" inset color="primary" v-model="ears" label="Ears"></v-checkbox>
        </v-col>
        <v-col cols="12" sm="3" md="3">
          <v-checkbox class="white--text" inset color="primary" v-model="nose" label="Nose"></v-checkbox>
        </v-col>
        <v-col cols="12" sm="3" md="3">
          <v-checkbox class="white--text" inset color="primary" v-model="mouth" label="Mouth"></v-checkbox>
        </v-col>
      </v-row>
    </v-card>
      <v-btn style="background-color:#01DFA5;color:whitesmoke;margin-top:30px;" @click="startDefacing">Start Defacing</v-btn>
    </div>
</div>
</template>

<script>
// import
import Vue from 'vue'
import MdButton from 'vue-material'
import dwv from 'dwv'
import axios from "axios";
//import http from "../plugins/http-common";

Vue.use(MdButton)

// gui overrides

// get element
dwv.gui.getElement = dwv.gui.base.getElement

// Image decoders (for web workers)
dwv.image.decoderScripts = {
  'jpeg2000': 'assets/dwv/decoders/pdfjs/decode-jpeg2000.js',
  'jpeg-lossless': 'assets/dwv/decoders/rii-mango/decode-jpegloss.js',
  'jpeg-baseline': 'assets/dwv/decoders/pdfjs/decode-jpegbaseline.js',
  'rle': 'assets/dwv/decoders/dwv/decode-rle.js'
}

export default {
  name: 'dwv',
  components: {
  },
  props: ['isLoad'],
  data: function () {
    return {
      ears: true,
      eyes: true,
      nose: true,
      mouth: true,
      versions: {
        dwv: dwv.getVersion(),
        vue: Vue.version
      },
      dwvApp: null,
      tools: {
        Scroll: {},
        ZoomAndPan: {},
        WindowLevel: {},
        Draw: {
          options: ['Ruler'],
          type: 'factory',
          events: ['draw-create', 'draw-change', 'draw-move', 'draw-delete']
        }
      },
      selectedTool: 'Select Tool',
      loadProgress: 0,
      dataLoaded: false,
      metaData: null,
      showDicomTags: true,
      dropboxClassName: 'dropBox',
      borderClassName: 'dropBoxBorder',
      hoverClassName: 'hover',
      file: null,
      files: [],
      index: 0,
    }
  },
  mounted () {
    // create app
    this.dwvApp = new dwv.App()
    // initialise app
    this.dwvApp.init({
      'containerDivId': 'dwv',
      'tools': this.tools,
    })

    // handle load events
    let nReceivedError = null;
    let nReceivedAbort = null;
    this.dwvApp.addEventListener('load-start', (/*event*/) => {
      this.dataLoaded = false;
      nReceivedError = 0;
      nReceivedAbort = 0;
    })
    this.dwvApp.addEventListener('load-progress', (event) => {
      this.loadProgress = event.loaded
    })
    this.dwvApp.addEventListener('load', (/*event*/) => {
      // set dicom tags
      this.metaData = dwv.utils.objectToArray(this.dwvApp.getMetaData());
      // set the selected tool
      let selectedTool = 'Scroll'
      if (this.dwvApp.isMonoSliceData() && this.dwvApp.getImage().getNumberOfFrames() === 1) {
        selectedTool = 'ZoomAndPan'
      }
      this.onChangeTool(selectedTool)
      // set data loaded flag
      this.dataLoaded = true
    })
    this.dwvApp.addEventListener('load-end', (/*event*/) => {
      if (nReceivedError) {
        this.loadProgress = 0
        alert('Received errors during load. Check log for details.')
      }
      if (nReceivedAbort) {
        this.loadProgress = 0
        alert('Load was aborted.')
      }
    })
    this.dwvApp.addEventListener('error', (/*event*/) => {
      //console.error(event.error)
      ++nReceivedError
    })
    this.dwvApp.addEventListener('abort', (/*event*/) => {
      ++nReceivedAbort
    })

    // handle key events
    this.dwvApp.addEventListener('keydown', (event) => {
        this.dwvApp.defaultOnKeydown(event)
    })
    // handle window resize
    window.addEventListener('resize', this.dwvApp.onResize)

    // setup drop box
    this.setupDropbox()

    // possible load from location
    dwv.utils.loadFromUri(window.location.href, this.dwvApp)
  },
  methods: {
    onChangeTool: function (tool) {
      this.selectedTool = tool
      this.dwvApp.setTool(tool)
      if (tool === 'Draw') {
        this.onChangeShape(this.tools.Draw.options[0]);
      }
    },
    onChangeShape: function (shape) {
      if ( this.dwvApp && this.selectedTool === 'Draw') {
        this.dwvApp.setDrawShape(shape);
      }
    },
    onReset: function () {
      this.dwvApp.resetDisplay()
    },
    setupDropbox () {
        // start listening to drag events on the layer container
        const layerContainer = this.dwvApp.getElement('layerContainer');
        if (layerContainer) {
          layerContainer.addEventListener('dragover', this.onDragOver);
          layerContainer.addEventListener('dragleave', this.onDragLeave);
          layerContainer.addEventListener('drop', this.onDrop);
        }
        // set the initial drop box size
        const box = this.dwvApp.getElement(this.dropboxClassName);
        if (box) {
          const size = this.dwvApp.getLayerContainerSize();
          const dropBoxSize = 2 * size.height / 3;
          box.setAttribute(
            'style',
            'width:' + dropBoxSize + 'px;height:' + dropBoxSize + 'px');
        }
    },
    onDragOver: function (event) {
      // prevent default handling
      event.stopPropagation();
      event.preventDefault();
      // update box border
      const box = this.dwvApp.getElement(this.borderClassName);
      if (box && box.className.indexOf(this.hoverClassName) === -1) {
        box.className += ' ' + this.hoverClassName;
      }
    },
    onDragLeave: function (event) {
      // prevent default handling
      event.stopPropagation();
      event.preventDefault();
      // update box class
      const box = this.dwvApp.getElement(this.borderClassName + ' hover');
      if (box && box.className.indexOf(this.hoverClassName) !== -1) {
        box.className = box.className.replace(' ' + this.hoverClassName, '');
      }
    },
    hideDropbox: function () {
      // remove box
      const box = this.dwvApp.getElement(this.dropboxClassName);
      if (box) {
        box.parentNode.removeChild(box);
      }
    },
    onDrop: function (event) {
      // prevent default handling
      event.stopPropagation();
      event.preventDefault();
      // load files
      this.dwvApp.loadFiles(event.dataTransfer.files);
      this.file = event.dataTransfer.files[0];
      // hide drop box
      this.hideDropbox();
    },
    setOver: function (data) {
      this.$parent.setOverlay = data;
    },
    startDefacing: async function () {
      let parts = [
        (this.eyes === true?1:0),
        (this.nose === true?1:0),
        (this.ears === true?1:0),
        (this.mouth === true?1:0)
      ];
      
      if(this.files.length < 1){
        alert("Please, select dicom file first.");
        return;
      }

      var formData = new FormData();

      for(var i = 0 ; i < this.files.length ; i++){
        formData.append('files', this.files[i]);
      }

      // set files option
      formData.append('type', 'dicom');
      formData.append('parts', parts);
      formData.append('prefix', 'did');


      //formData.append("files", this.files);
      console.log(formData);
      this.$parent.setOverlay(true);

      try{
        var response = await axios.post('http://localhost:3000/api/deface', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log(response)
        this.$parent.destPath = response.data.filePath;
        this.$parent.resultFileList = response.data.files;
        this.$parent.resultUrl = response.data.download;
        console.log(this.$parent.destPath);
        this.$parent.setOverlay(false);
      }catch(error){
        alert("Failed to deface your MRI data. Please try it again or another data.")
        this.$parent.setOverlay(false);
      }
      
    },
    next: function() {
      if(this.index+1 < this.files.length-1){
        this.index = this.index+1;
        this.file = this.files[this.index];
        this.dwvApp.loadFiles([this.file]);
      }else{
        console.log("end");
      }
    },
    prev: function() {
      if(this.index != 0){
        this.index = this.index-1;
        this.file = this.files[this.index];
        this.dwvApp.loadFiles([this.file]);
      }else{
        console.log("first");
      }
    },
  },
  watch: {
    /*file: function() {
      this.dwvApp.loadFiles(event.target.files);
      this.hideDropbox();
    },*/
    files: function() {
      this.file = this.files[this.index];
      console.log(this.file);
      this.dwvApp.loadFiles([this.file]);
      this.hideDropbox();
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#dwv {
  font-family: Arial, Helvetica, sans-serif;
  text-align: center;
  height: 90%; }

h1 {
  font-size: 1.5em;
  padding-top: 20px;
  padding-bottom: 15px;
}


element.style {
    width: 248px;
    height: 248px;
}

/* Layers */
.layerContainer {
    position: relative; padding: 0;
    height: 400px;
    margin: auto; margin-bottom: 5em;text-align: center; }
.imageLayer {
    position: absolute;
    left: 0px; }
.drawDiv {
    position: absolute; pointer-events: none; }

/* drag&drop */
.dropBox {
    border: 5px dashed rgba(68,138,255,0.38);
    width: 248px;
    height: 248px;
    margin: auto;
    text-align: center; vertical-align: center; }
.dropBox.hover { border: 5px dashed var(--md-theme-default-primary); }


</style>
