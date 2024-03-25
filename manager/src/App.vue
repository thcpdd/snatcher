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
                    <el-sub-menu index="1">
                        <template #title>
                            <span>选课数据</span>
                        </template>
                        <el-menu-item index="/all"><span>全部选课数据</span></el-menu-item>
                        <el-menu-item index="/fail"><span>选课失败数据</span></el-menu-item>
                        <el-menu-item index="/code"><span>抢课码信息</span></el-menu-item>
                    </el-sub-menu>
                    <el-sub-menu index="2">
                        <template #title>
                            <span>课程信息</span>
                        </template>
                        <el-menu-item index="/pe"><span>体育课课程信息</span></el-menu-item>
                        <el-menu-item index="/pc"><span>公选课课程信息</span></el-menu-item>
                    </el-sub-menu>
                </el-menu>
            </el-col>
        </el-row>
    </div>
    <div v-if="isLogin" class="status">
        <span>管理员：{{ username }}&emsp;|&emsp;</span>
        <el-button @click="logout" type="danger" size="small">注销</el-button>
    </div>
    <div class="content">
        <router-view></router-view>
    </div>
</template>

<script setup>
import {RouterView} from "vue-router";
import {onBeforeMount, ref} from "vue";
import router from "@/router/index.js";

const username = ref('')
const isLogin = ref(false)
onBeforeMount(() => {
    let token = localStorage.getItem('token')
    if(!token) {
        router.push('/login')
    } else {
        let pyload = JSON.parse(window.atob(token.split('.')[1]))
        let exp = pyload.exp
        if (Date.parse(Date()) / 1000 > exp) {  // 过期
            localStorage.removeItem('token')
            window.location = '/login'
        }
        username.value = pyload.username
        isLogin.value = true
    }
})

const logout = () => {
    localStorage.removeItem('token')
    window.location = '/login'
    isLogin.value = false
}
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
    margin-top: 13px;
    background-color: white;
    margin-right: 16px;
}
.status {
    float: right;
    margin-right: 20px;
    margin-top: 14px;
    font-size: 17px;
}
</style>
