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
    let _isLogin = sessionStorage.getItem('isLogin')
    if(!_isLogin) {
        router.push('/login')
    } else {
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
    border: 1px solid #cbccce;
    border-radius: 10px;
    text-align: -webkit-center;
    float: right;
    margin-top: 17px;
}
</style>
