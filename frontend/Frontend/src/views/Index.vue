<template>
    <div class="index-content">
        <div>
            <div class="t1">
                <span class="t1-font">
                    Snatcher<br/>基于定时任务队列的
                </span>
            </div>
            <div class="t2"><span class="t2-font">Python Spider Program</span></div>
            <div class="t3"><span>傻瓜式操作：选择课程-输入信息-提交</span></div>
            <div style="margin-top: 4%">
                <el-button type="primary"
                           style="width: max-content;font-weight: bolder;font-size: 15px"
                           @click="router.push('/pc')"
                           size="large"
                >开始预约抢课</el-button>
            </div>
        </div>
    </div>
    <div class="frontend-technology">
        <div>
            <div class="tc1"><span class="tc1-font">Vue3 + Element-Plus</span></div>
            <div class="tc2">
                <span>
                    以Vite为脚手架，将整个WEB界面打包成静态文件，通过Nginx服务器进行部署，<br/>
                    从而减少了页面一系列不必要的编译时间，提高了页面的流畅度。
                </span>
            </div>
            <div class="tc2">
                <span>
                    使用Element-Plus快速构建WEB界面。
                </span>
            </div>
        </div>
    </div>
    <div class="backend-technology">
        <div>
            <div><span class="bt1-font">FastAPI + MySQL + Redis + Celery</span></div>
            <div class="tc2">
                <span>
                    FastAPI是现代的Python后端框架，以其天生异步的特性成名。
                </span>
            </div>
            <div class="tc2">
                <span>
                    以MySQL作为存储数据库，Redis作为缓存后端结合Celery实现异步定时任务。
                </span>
            </div>
            <div class="tc2">
                <span>
                    前后端分离部署方案。
                </span>
            </div>
        </div>
    </div>
</template>

<script setup>
import router from "@/router/index.js";
</script>

<style>
.index-content {
    background: linear-gradient(0deg, #d3f2fa 20%, #c4cefa);
    height: 100vh;
}
.index-content div{
    position: relative;
    top:50%;
    transform:translateY(-50%);
}
.t1-font {
    font-size: 70px;
    background: linear-gradient(315deg, #4760ff 50%,#66e7fc);
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: "方正艺黑简体", monospace;
}
.t2-font {
    font-size: 45px;
    font-weight: bold;
    font-family: "Segoe UI Black", monospace;
    color: #2a2929;
}
.t3 {
    margin-top: 1%;
    font-size: 21px;
    font-weight: bold;
}

.frontend-technology {
    background: linear-gradient(0deg, #d7f3fa 35%, #a2ccff);
    height: 100vh;
}
.frontend-technology div {
    position: relative;
    top:50%;
    transform:translateY(-50%);
}
.tc1-font {
    font-size: 55px;
    font-weight: bolder;
    color: #42b883;
}
.tc2 {
    font-weight: bold;
    margin-top: 14px;
    font-size: 20px;
}

.backend-technology {
    height: 100vh;
    background-color: #e4f3f6;
}
.backend-technology div {
    position: relative;
    top:50%;
    transform:translateY(-50%);
}
.bt1-font {
    font-size: 55px;
    font-weight: bolder;
    color: #42b883;
}
</style>
