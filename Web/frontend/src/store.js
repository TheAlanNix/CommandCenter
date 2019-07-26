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
    SET_ERRORS(state, errors) {
      state.errors = errors;
    },
    SET_EVENTS(state, events) {
      state.events = events;
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
    fetchEvents(context) {
      // Clear any existing timeout
      clearTimeout(this.state.timeout);

      // Indicate that we're loading
      context.commit('SET_LOADING_STATUS', true);

      // Get the event data
      const path = `http://${window.location.hostname}:5000/api/events?timeframe=${this.state.timeframe}`;
      console.log(path);
      axios.get(path)
        .then((res) => {
          console.log(res.data);
          context.commit('SET_EVENTS', res.data.events);
          context.commit('SET_LOADING_STATUS', false);
          context.commit('SET_TIMEOUT', setTimeout(() => {
            context.dispatch('fetchEvents');
          }, 30000));
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          context.commit('ADD_ERROR', { message: error });
          context.commit('SET_LOADING_STATUS', false);
          context.commit('SET_TIMEOUT', setTimeout(() => {
            context.dispatch('fetchEvents');
          }, 30000));
        });
    },
  },
});
