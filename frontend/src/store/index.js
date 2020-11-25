import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    isLoad: false,
  },
  mutations: {
    setLoad: function(state, isLoad){
      this.state.isLoading = isLoad;
    }
  },
  actions: {
  },
  modules: {
  },
  getter: {
    getLoad: function(state){
      return state.isLoad;
    }
  }
})
