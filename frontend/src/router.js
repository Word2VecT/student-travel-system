import { createRouter, createWebHistory } from 'vue-router';
import Detail from './components/Detail.vue';
import Home from './components/Home.vue';
import LoginRegister from './components/LoginRegister.vue';

const routes = [
    { path: '/', component: LoginRegister },
    { path: '/home', component: Home },
    { path: '/detail/:id', component: Detail },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
