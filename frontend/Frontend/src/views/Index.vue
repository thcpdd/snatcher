<template>
    <div id="page1"></div>
    <div class="index-content">
        <div class="t1">
            <span class="t1-font">
                Snatcher<br/>基于定时任务队列的
            </span>
        </div>
        <div class="t2"><span class="t2-font">Python Spider Program</span></div>
        <div class="t3"><span>选择课程-填写相关信息-提交-预约抢课成功</span></div>
        <div style="margin-top: 3%">
            <el-button type="primary"
                       style="width: max-content;font-weight: bolder;font-size: 100%"
                       @click="router.push('/pc')"
                       size="large"
                       class="to-book"
            >开始预约抢课 &gt;&gt;&gt;</el-button>
        </div>
        <a href="/#page2" class="next-page" style="top: 100%" title="下一页">↓</a>
    </div>
    <div id="page2"></div>
    <div class="frontend-technology">
        <div class="tc1"><span class="tc1-font">Vue3 + Element-Plus</span></div>
        <div class="tc2">
            <span>
                以Vite为脚手架，将整个WEB界面打包成静态文件，部署在Nginx服务器，<br/>
                从而减少一系列不必要的编译时间，提高了页面的流畅度。<br/>
            </span>
        </div>
        <div class="tc2">
            <span>使用Element-Plus快速构建WEB UI界面。</span>
        </div>
        <div class="logo-image">
            <img src="/vue-logo.svg" alt="vue-logo" style="width: 10%;margin-right: 3%">
            <img src="/vite-logo.svg" alt="vite-logo" style="width: 10%">
        </div>
        <div class="logo-image">
            <img src="/nginx.png" alt="nginx" style="width: 50%"><br/><br/>
            <img src="/element-plus-logo.svg" alt="element-plus-logo" style="width: 50%">
        </div>
        <a href="/#page3" class="next-page" style="top: 200%" title="下一页">↓</a>
    </div>
    <div id="page3"></div>
    <div class="backend-technology">
        <div><span class="bt1-font">FastAPI + MySQL + Redis + Celery</span></div>
        <div class="tc2">
            <span>
                FastAPI是现代的Python后端框架，是当今最快的Python后端框架之一。
            </span>
        </div>
        <div class="tc2">
            <span>
                以MySQL作为存储数据库，Redis作为缓存后端结合Celery实现异步定时任务。
            </span>
        </div>
        <div class="logo-image">
            <img src="/logo-mysql-170x115.png" alt="mysql-logo" style="width: 15%"><br/>
            <img src="/fastapi.png" alt="fastapi-logo" style="width: 30%"><br/>
            <img src="/redis_original_logo_icon_146368.svg" alt="redis-logo" style="width: 8%">
            <img src="/celery_512.webp" alt="celery-logo" style="width: 8%;margin-left: 3%">
        </div>
    </div>
</template>

<script setup>
import router from "@/router/index.js";
import {onMounted} from "vue";

let width = window.innerWidth;
function setFontSize(selector, rate) {
    document.querySelector(selector).style.fontSize = width / rate + "px";
}
onMounted(() => {
    // 重新调整移动端的字体大小
    if (sessionStorage.getItem("isMobile")) {
        setFontSize(".t1-font", 10);
        setFontSize(".t2-font", 17);
        setFontSize(".t3", 27);
        setFontSize(".tc1-font", 13)
        setFontSize(".tc2", 20)
        setFontSize(".bt1-font", 18)
    }
})
</script>

<style>
@font-face {
    font-family: "fangzhen";
    src: url("/方正艺黑简体_0.ttf");
}
.index-content {
    background: linear-gradient(0deg, #d3f2fa 20%, #c4cefa);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    flex-direction: column;
}
.t1 {
    margin-top: 5%;
}
.t1-font {
    font-size: 500%;
    background: linear-gradient(315deg, #4760ff 50%,#66e7fc);
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: "fangzhen", monospace;
}
.t2 {
    margin-top: 1%;
}
.t2-font {
    font-size: 300%;
    font-weight: bold;
    font-family: "Segoe UI Black", monospace;
    color: #2a2929;
}
.t3 {
    margin-top: 2%;
    font-size: 150%;
    font-weight: bold;
}

.frontend-technology {
    background: linear-gradient(0deg, #d7f3fa 35%, #a2ccff);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    height: 100vh;
    overflow: auto;
}
.tc1-font {
    font-size: 320%;
    font-weight: bolder;
    color: #42b883;
}
.tc2 {
    font-weight: bold;
    margin-top: 14px;
    font-size: 120%;
}

.backend-technology {
    height: 100vh;
    background-color: #e4f3f6;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    flex-direction: column;
}
.bt1-font {
    font-size: 320%;
    font-weight: bolder;
    color: #42b883;
}
.logo-image {
    margin-top: 1.5%;
}
.next-page {
    position: absolute;
    text-align: center;
    text-decoration: none;
    font-size: 180%;
    color: black;
}
</style>
