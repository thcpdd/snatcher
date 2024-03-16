<template>
    <el-drawer
        :model-value="openDrawer"
        title="提交你的选课信息"
        direction="btt"
        size="80%"
        @close="closeHandle"
    >
        <div class="selected-course">
            <span style="font-weight: bolder">你的意向课程：</span>
            <p v-for="data in currentSelecting">{{ data.courseName }}</p>
        </div>
        <h3>为了您更好的体验，我们需要收集你的一些信息。</h3>
        <div class="user-info-box">
            <div class="user-info">
                <span>学号：</span>
                <el-input v-model="username" style="width: 40%" placeholder="请输入你的学号"/>
            </div>
            <div class="user-info">
                <span>密码：</span>
                <el-input v-model="password" style="width: 40%" type="password" :show-password="true" placeholder="请输入你的密码"/>
            </div>
            <div class="user-info">
                <span>邮箱：</span>
                <el-input v-model="email" style="width: 40%" placeholder="请输入你的邮箱"/>
            </div>
        </div>
        <p>**请确保所填信息完全正确，选课结果将会发送到该邮箱。</p>
        <el-button type="primary" @click="submitSelected" :disabled="!canBeSubmitted">提交</el-button>
    </el-drawer>
</template>

<script setup>
import {ref, defineProps, defineEmits, computed} from 'vue'
import { ElMessage } from 'element-plus'

const username = ref('')
const password = ref('')
const email = ref('')
const canBeSubmitted = computed(() => {
    return username.value !== '' && password.value !== '' && email.value !== ''
})

// 接收父组件传来的参数
defineProps({
    openDrawer: Boolean,
    currentSelecting: Array
})

// 通知父组件修改新的值
const changeOpenDrawer = defineEmits(['update:openDrawer'])
function closeHandle() {
    changeOpenDrawer('update:openDrawer', false)
}

function submitSelected() {
    ElMessage({
        message: '预约信息提交成功！',
        type: 'success',
        showClose: true
  })
}
</script>

<style>
.selected-course {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    background-color: aliceblue;
    padding-top: 17px;
    padding-bottom: 8px;
    width: 35%;
}
.user-info {
    margin-bottom: 10px;
}
.user-info-box {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    width: 35%;
    padding-bottom: 4px;
    padding-top: 13px;
    background-color: aliceblue;
}
</style>
