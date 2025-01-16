import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/Home.vue';
import DataPlotPage from '../components/ExamplePlot.vue';

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage,
    },
    {
        path: '/plot',
        name: 'DataPlot',
        component: DataPlotPage,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
