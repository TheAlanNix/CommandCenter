import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    errors: [],
    events: [],
    loading: false,
    timeframe: 6,
    timeout: null,
  },
  mutations: {
    ADD_ERROR(state, error) {
      state.errors.push(error);
    },
    DELETE_ERROR(state, errorIndex) {
      state.errors.splice(errorIndex, 1);
    },
    SET_ERRORS(state, errors) {
      state.errors = errors;
    },
    SET_EVENTS(state, events) {
      state.events = events;
    },
    CLEAR_TIMEOUT(state) {
      clearTimeout(state.timeout);
      state.timeout = null;
    },
    SET_TIMEOUT(state, timeout) {
      state.timeout = timeout;
    },
    SET_LOADING_STATUS(state, status) {
      state.loading = status;
    },
    SET_TIMEFRAME(state, timeframe) {
      state.timeframe = timeframe;
    },
  },
  actions: {
    addError(context, error) {
      context.commit('ADD_ERROR', error);
    },
    deleteError(context, errorIndex) {
      context.commit('DELETE_ERROR', errorIndex);
    },
    setTimeframe(context, timeframe) {
      context.commit('SET_TIMEFRAME', timeframe);
    },
    clearTimeout(context) {
      // Clear any existing timeout
      context.commit('CLEAR_TIMEOUT');
    },
    setTimeout(context, timeout) {
      context.commit('SET_TIMEOUT', timeout);
    },
    getEvents(context, hostIp) {
      // Clear any existing timeout
      context.commit('CLEAR_TIMEOUT');

      // Indicate that we're loading
      context.commit('SET_LOADING_STATUS', true);

      // Get the event data
      let path = `http://${window.location.hostname}:5000/api/events?timeframe=${this.state.timeframe}`;
      if (hostIp) path = `${path}&host_ip=${encodeURIComponent(hostIp)}`;
      console.log(path);
      axios.get(path)
        .then((res) => {
          context.commit('SET_EVENTS', res.data.events);
          context.commit('SET_LOADING_STATUS', false);
        })
        .catch((error) => {
          console.error(error);
          context.commit('ADD_ERROR', { message: error });
          context.commit('SET_LOADING_STATUS', false);
        });
    },
  },
});
