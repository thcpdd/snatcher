import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router/index.js";
import 'element-plus/dist/index.css'
import 'nprogress/nprogress.css'


// 防止用户通过快捷键打开控制台
document.addEventListener("keydown", function (event) {
    if (event.key === "F12" || (event.ctrlKey && event.shiftKey && event.key === "I")) {
        event.preventDefault();  // 阻止默认行为（打开控制台）
    }
});

// 禁用右键菜单
document.addEventListener("contextmenu", function (event) {
    event.preventDefault();  // 阻止右键菜单弹出
});


const app = createApp(App)

app.use(router)
app.mount('#app')
