import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router/index.js";
import 'element-plus/dist/index.css'
import 'nprogress/nprogress.css'
import { requests } from "@/request.js";


// 动态设置 axios 的 baseUrl，以适应不同的部署环境。
const prepare = async () => {
    if (!requests.defaults.baseURL) {
        let url = sessionStorage.getItem('url')
        if (!url) {
             await requests.get('https://rainbow.hi.cn/snatcherapi').then((res) => {
                url = res.data.url
                sessionStorage.setItem('url', url)
            })
        }
        requests.defaults.baseURL = url
    }
}


const app = createApp(App)

app.provide('prepare', prepare)
app.use(router)
app.mount('#app')
