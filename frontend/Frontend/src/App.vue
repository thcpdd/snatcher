<template>
    <el-menu
        :default-active="defaultPage"
        class="el-menu-demo"
        mode="horizontal"
        :ellipsis="false"
        @select="handleSelect"
        :router="true"
    >
        <img src="/snatcher.png" alt="Snatcher logo" title="Snatcher logo"/>
        <div class="flex-grow"/>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/pc">公选课</el-menu-item>
        <el-menu-item index="/pe">体育课</el-menu-item>
    </el-menu>
    <div class="content">
        <RouterView/>
    </div>
</template>

<script setup>
    import {ref} from 'vue'
    import {RouterView} from 'vue-router'

    const defaultPage = ref('/')
    const handleSelect = (key, keyPath) => {
        console.log(key, keyPath)
    }

</script>

<style>
    body {
        margin: 0;
    }
    .flex-grow {
        flex-grow: 1;
    }
    .content {
        border: 1px solid #d3d3d3;
        border-radius: 10px;
        text-align: -webkit-center;
        margin-top: 10px;
        padding-bottom: 13px;
    }
    .paginator {
        margin-bottom: 15px;
        margin-left: 43%;
    }
    .el-menu-demo {
        background-color: #f4f6f8;
        border-radius: 10px;
    }
</style>
