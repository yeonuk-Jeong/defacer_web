import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'

import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'
import vuetify from './plugins/vuetify';
import '@babel/polyfill'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'
import VueResource from 'vue-resource';
//import store from './store'

Vue.use(VueResource);
Vue.config.productionTip = false

new Vue({
  //store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
