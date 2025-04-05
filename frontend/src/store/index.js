import { createStore } from 'vuex'

export default createStore({
  state: {
    uploadedFile: null,
    fileValidationInfo: null,
    fileData: [],
    lastPredictionResult: null
  },
  mutations: {
    setUploadedFile(state, file) {
      state.uploadedFile = file
    },
    setFileValidationInfo(state, info) {
      state.fileValidationInfo = info
    },
    setFileData(state, data) {
      state.fileData = data
    },
    setPredictionResult(state, result) {
      state.lastPredictionResult = result
    },
    clearUploadedFile(state) {
      state.uploadedFile = null
      state.fileValidationInfo = null
      state.fileData = []
      state.lastPredictionResult = null
    }
  },
  actions: {
    saveUploadFile({ commit }, { file, validationInfo }) {
      commit('setUploadedFile', file)
      commit('setFileValidationInfo', validationInfo)
    },
    saveFileData({ commit }, data) {
      commit('setFileData', data)
    },
    savePredictionResult({ commit }, result) {
      commit('setPredictionResult', result)
    }
  },
  getters: {
    getUploadedFile: state => state.uploadedFile,
    getFileValidationInfo: state => state.fileValidationInfo,
    getFileData: state => state.fileData,
    getLastPredictionResult: state => state.lastPredictionResult
  }
})