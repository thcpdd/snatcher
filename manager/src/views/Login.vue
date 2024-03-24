<template>
    <el-card class="login-form">
        <h3>验证管理员身份</h3>
        <el-form>
            <el-form-item>
                <el-input
                    placeholder="请输入管理员账号"
                    v-model="username"
                    style="padding-bottom: 4px"
                ></el-input>
            </el-form-item>
            <el-form-item>
                <el-input
                    placeholder="请输入管理员密码"
                    v-model="password"
                    style="padding-bottom: 4px"
                    type="password"
                    :show-password="true"
                ></el-input>
            </el-form-item>
        </el-form>
        <el-button type="primary" style="width: 100%" :disabled="!canBeLogin" @click="_login">登录</el-button>
    </el-card>
</template>

<script setup>
import {ref, computed} from "vue";
import {myMessage} from "@/message.js";
import {login} from "@/request.js";


const username = ref("");
const password = ref("");
const canBeLogin = computed(() => {
    return username.value !== "" && password.value !== "";
});

const _login = async () => {
    let res = await login(username.value, password.value)
    if (res.success) {
        window.location = '/'
    } else {
        myMessage(res.msg, 'error')
    }
}
</script>

<style>
.login-form {
    width: 400px;
    border-radius: 10px;
    margin-top: 12%;
    margin-right: 15%;
}
body {
    background-repeat: no-repeat;
    background-size: cover;
    background-image: url("/wallhaven-72yzje.jpg");
}
.content {
    background-color: unset;
}
</style>
