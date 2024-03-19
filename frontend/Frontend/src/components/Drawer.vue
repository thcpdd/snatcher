<template>
    <el-drawer
        :model-value="openDrawer"
        title="提交你的选课信息"
        direction="btt"
        size="80%"
        @close="emits('update:openDrawer', false)"
    >
        <div class="selected-course">
            <span style="font-weight: bolder">你的意向课程：</span>
            <p v-for="course in currentSelecting">
                {{ course.course_name }}
                <el-button
                    type="danger"
                    size="small"
                    @click="expectDelete = course.course_id"
                >撤销</el-button>
            </p>
        </div>
        <h3>为了您更好的体验，我们需要收集你的一些信息。</h3>
        <div class="user-info-box">
            <div class="user-info">
                <span>&nbsp;&nbsp;&nbsp;学号：</span>
                <el-input v-model="username" style="width: 65%" placeholder="请输入你的学号"/>
            </div>
            <div class="user-info">
                <span>&nbsp;&nbsp;&nbsp;密码：</span>
                <el-input v-model="password" style="width: 65%" type="password" :show-password="true" placeholder="请输入你的密码"/>
            </div>
            <div class="user-info">
                <span>&nbsp;&nbsp;&nbsp;邮箱：</span>
                <el-input v-model="email" style="width: 65%" placeholder="请输入你的邮箱"/>
            </div>
            <div class="user-info">
                <span>抢课码：</span>
                <el-input v-model="verifyCode" style="width: 65%" placeholder="请输入提供给你的抢课码"/>
            </div>
        </div>
        <p>**请确保所填信息完全正确，选课结果将会发送到该邮箱。</p>
        <el-button type="primary" @click="submitSelected" :disabled="!canBeSubmitted">提交</el-button>
    </el-drawer>
</template>

<script setup>
import {ref, defineProps, defineEmits, computed, watch} from 'vue'
import {myMessage} from "@/message.js";
import {bookCourse} from "@/request.js";

const username = ref('')
const password = ref('')
const email = ref('')
const verifyCode = ref('')
// 记录要撤销的课程
const expectDelete = ref(null)
// 判断当前输入是否能提交
const canBeSubmitted = computed(() => {
    return username.value !== '' &&
        password.value !== '' &&
        email.value !== '' &&
        props.currentSelecting.length > 0 &&
        verifyCode.value !== ''
})

// 接收父组件传来的参数
const props = defineProps({
    openDrawer: Boolean,
    currentSelecting: Array
})
// 自定义事件
const emits = defineEmits(['update:openDrawer', 'update:currentSelecting'])

// 监听用户点击“撤销”按钮
watch(expectDelete, (course_id) => {
    let newCurrentSelecting = []
    // 防止递归调用
    if (course_id === null) {
        return
    }
    props.currentSelecting.forEach((course) => {
        if (course.course_id !== course_id) {
            newCurrentSelecting.push(course)
        }
    })
    emits('update:currentSelecting', newCurrentSelecting)
    if (newCurrentSelecting.length === 0) {
        emits('update:openDrawer', false)
    }
    expectDelete.value = null
})

async function submitSelected() {
    let pathName = location.pathname
    let data = {
        username: username.value,
        password: password.value,
        email: email.value,
        courses: props.currentSelecting,
        verify_code: verifyCode.value
    }
    const responseData = await bookCourse(pathName, data)
    if (responseData.success === 1) {
        myMessage('预约信息提交成功！', 'success')
        emits('update:openDrawer', false)
        emits('update:currentSelecting', [])
    } else {
        myMessage(responseData.msg, 'error')
    }
}
</script>

<style>
.selected-course {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    background-color: aliceblue;
    padding-top: 17px;
    padding-bottom: 8px;
    width: 95%;
}
.user-info {
    margin-bottom: 10px;
}
.user-info-box {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    width: 95%;
    padding-bottom: 4px;
    padding-top: 13px;
    background-color: aliceblue;
}
</style>
