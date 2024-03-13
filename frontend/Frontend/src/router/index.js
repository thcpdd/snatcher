import {createRouter, createWebHistory} from "vue-router";
import PhysicalEducation from "@/views/PhysicalEducation.vue";
import PublicChoice from "@/views/PublicChoice.vue";
import Index from "@/views/Index.vue";


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

export default router
