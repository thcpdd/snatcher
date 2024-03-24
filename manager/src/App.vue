<template>
    <div v-if="isLogin" class="navigator">
        <img src="/snatcher.svg" alt="logo" style="max-width: 100%">
        <el-row class="tac">
            <el-col>
                <el-menu
                        default-active="/"
                        class="el-menu"
                        :router="true"
                >
                    <el-menu-item index="/"><span>首页</span></el-menu-item>
                    <el-menu-item index="/all"><span>全部选课数据</span></el-menu-item>
                    <el-menu-item index="/fail"><span>选课失败数据</span></el-menu-item>
                    <el-menu-item index="/code"><span>抢课码信息</span></el-menu-item>
                </el-menu>
            </el-col>
        </el-row>
    </div>
    <div class="content">
        <router-view></router-view>
    </div>
</template>

<script setup>
import {RouterView} from "vue-router";
import {onBeforeMount, ref} from "vue";
import router from "@/router/index.js";

const isLogin = ref(false)
onBeforeMount(() => {
    let token = localStorage.getItem('token')
    if(!token) {
        router.push('/login')
    } else {
        let exp = JSON.parse(window.atob(token.split('.')[1])).exp
        if (Date.parse(Date()) / 1000 > exp) {  // 过期
            localStorage.removeItem('token')
            window.location = '/login'
        }
        isLogin.value = true
    }
})
</script>

<style>
body {
    background-color: #f5f5f5;
}

.el-menu {
    width: 100%;
    --el-menu-bg-color: #f5f5f5;
}

.navigator {
    width: 13%;
    float: left;
    overflow: hidden;
}

.content {
    width: 85%;
    border-radius: 10px;
    text-align: -webkit-center;
    float: right;
    margin-top: 50px;
    background-color: white;
    margin-right: 16px;
}
</style>
