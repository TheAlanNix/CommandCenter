import Vue from 'vue';
import Router from 'vue-router';
import HostView from '@/components/HostView';
import SecurityEventsView from '@/components/SecurityEventsView';
import NotFound from '@/components/NotFound';
import Ping from '@/components/Ping';
import Splash from '@/components/Splash';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Splash',
      component: Splash,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
    {
      path: '/host/:host_ip',
      name: 'HostView',
      component: HostView,
      props: true,
    },
    {
      path: '/security-events',
      name: 'SecurityEvents',
      component: SecurityEventsView,
    },
    {
      path: '*',
      name: 'NotFound',
      component: NotFound,
    },
  ],
});
