<template>
    <el-menu
        :default-active="defaultPage"
        class="el-menu-demo"
        mode="horizontal"
        :ellipsis="false"
        @select="handleSelect"
        :router="true"
    >
        <el-menu-item index="0">
            <!--            <img-->
            <!--                    style="width: 100px"-->
            <!--                    src="/images/element-plus-logo.svg"-->
            <!--                    alt="Element logo"-->
            <!--            />-->
            <span style="font-size: 17px">Snatcher</span>
        </el-menu-item>
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
    .flex-grow {
        flex-grow: 1;
    }
    .content {
        border: 1px solid #d3d3d3;
        border-radius: 4px;
        text-align: -webkit-center;
        margin-top: 10px;
    }
    .paginator {
        margin-bottom: 15px;
        margin-left: 43%;
    }

</style>
