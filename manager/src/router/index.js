import {createRouter, createWebHistory} from "vue-router";


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'index',
            component: () => import('../views/Index.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/Login.vue')
        },
        {
            path: '/all',
            name: 'all',
            component: () => import('../views/All.vue')
        },
        {
            path: '/fail',
            name: 'fail',
            component: () => import('../views/Fail.vue')
        },
        {
            path: '/code',
            name: 'code',
            component: () => import('../views/Code.vue')
        }
    ]
})

export default router
