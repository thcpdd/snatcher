import {createRouter, createWebHistory} from "vue-router";
import PhysicalEducation from "@/views/PhysicalEducation.vue";
import PublicChoice from "@/views/PublicChoice.vue";
import Index from "@/views/Index.vue";
import NProgress from 'nprogress'


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'index',
            component: Index
        },
        {
            path: '/pc',
            name: 'pc',
            component: PublicChoice
        },
        {
            path: '/pe',
            name: 'pe',
            component: PhysicalEducation
        }
    ]
})

router.beforeEach((to, from, next) => {
    NProgress.start()
    next()
})

router.afterEach(() => {
    NProgress.done()
})

export default router
