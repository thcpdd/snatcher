<template>
    <el-menu
            :default-active="$route.path"
            class="el-menu-demo"
            mode="horizontal"
            :ellipsis="false"
            :router="true"
    >
        <img :src="imageUrl()" alt="Snatcher logo" title="Snatcher logo" style="overflow: hidden"/>
        <div class="flex-grow"></div>
        <el-menu-item index="/">首页</el-menu-item>
        <el-sub-menu>
            <template #title>👉预约抢课</template>
            <el-menu-item index="/pc">公选课</el-menu-item>
            <el-menu-item index="/pe">体育课</el-menu-item>
        </el-sub-menu>
        <img src="https://q.qlogo.cn/headimg_dl?dst_uin=1834763300&spec=640&img_type=jpg" class="avatar" alt="avatar">
    </el-menu>
    <div class="content">
        <RouterView/>
    </div>
</template>

<script setup>
import { RouterView } from 'vue-router'

const imageUrl = () => {
    let isMobile = navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i)
    if (isMobile) {
        sessionStorage.setItem('isMobile', '1')
        return '/logo.png'
    }
    return '/snatcher.svg'
}
</script>

<style>
body, html {
    margin: 0;
    scroll-behavior: smooth;
}
.flex-grow {
    flex-grow: 1;
}
.content {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    text-align: -webkit-center;
    margin-top: 10px;
    overflow: hidden;
    height: max-content;
}
.el-menu-demo {
    border-radius: 10px;
    overflow: clip;
    --el-menu-bg-color: #f4f6f8 /*官方文档写的就是一坨*/
}
.avatar {
    border-radius: 50%;
    height: 80%;
    margin-top: 8px;
    margin-right: 10px;
}
/* 隐藏垂直滚动条 */
body::-webkit-scrollbar {
    width: 0;  /* 设置为0，完全隐藏滚动条 */
    /*height: 0; !* 同样适用于水平滚动条 *!*/
}

/* 隐藏滚动条的轨道 */
body::-webkit-scrollbar-track {
    background: transparent;
}

/* 隐藏滚动条的滑块 */
body::-webkit-scrollbar-thumb {
    background: transparent;
}
</style>
