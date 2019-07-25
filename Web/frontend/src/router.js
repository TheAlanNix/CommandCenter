import Vue from 'vue';
import Router from 'vue-router';
import Host from './views/Host.vue';
import NotFound from './views/NotFound.vue';
import Ping from './views/Ping.vue';
import SecurityEvents from './views/SecurityEvents.vue';
import Splash from './views/Splash.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'splash',
      component: Splash,
    },
    {
      path: '/host/:hostIp',
      name: 'host',
      component: Host,
      props: true,
    },
    {
      path: '/ping',
      name: 'ping',
      component: Ping,
    },
    {
      path: '/security-events',
      name: 'security-events',
      component: SecurityEvents,
    },
    {
      path: '*',
      name: 'NotFound',
      component: NotFound,
    },
  ],
});
