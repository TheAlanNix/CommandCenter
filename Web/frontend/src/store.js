import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    errors: [],
    events: [],
    loading: false,
    notification: null,
    timeframe: 6,
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
    ADD_NOTIFICATION(state, notification) {
      state.notification = notification;
    },
    DELETE_NOTIFICATION(state) {
      state.notification = null;
    },
    SET_EVENTS(state, events) {
      state.events = events;
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
    addNotification(context, notification) {
      context.commit('ADD_NOTIFICATION', notification);
    },
    deleteNotification(context) {
      context.commit('DELETE_NOTIFICATION');
    },
    setTimeframe(context, timeframe) {
      context.commit('SET_TIMEFRAME', timeframe);
    },
    getEvents(context, hostIp) {
      // Clear any existing timeout
      // context.commit('CLEAR_TIMEOUT');

      // Indicate that we're loading
      context.commit('SET_LOADING_STATUS', true);

      // Get the event data
      let path = `http://${window.location.hostname}:5000/api/events?timeframe=${this.state.timeframe}`;
      if (hostIp) path = `${path}&host_ip=${encodeURIComponent(hostIp)}`;
      console.log(path);
      axios.get(path, { timeout: 60000 })
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
