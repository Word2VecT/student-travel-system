import { createRouter, createWebHistory } from 'vue-router';

const routes = [
    { path: '/', component: () => import('./components/LoginRegister.vue') },
    { path: '/home', component: () => import('./components/Home.vue') },
    { path: '/detail/:id', component: () => import('./components/Detail.vue') },
    { path: '/travel/:id', component: () => import('./components/Travel.vue') },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
