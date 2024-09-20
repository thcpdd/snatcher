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
            <el-form
                v-model="form"
                label-width="auto"
                style="width: 85%"
                :label-position="labelPosition"
            >
                <el-form-item label="登录方式" required>
                    <el-radio-group v-model="form.loginMethod">
                        <el-radio value="1">学号密码</el-radio>
                        <el-radio value="2">Cookie</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="学号" required>
                   <el-input v-model="form.username" placeholder="请输入学号"/>
                </el-form-item>

                <el-form-item v-if="form.loginMethod === '1'" label="密码" required>
                   <el-input v-model="form.password" placeholder="请输入密码" type="password"/>
                </el-form-item>
                <div v-else>
                    <el-form-item label="Cookie" required>
                       <el-input v-model="form.cookie" placeholder="请输入Cookie"/>
                    </el-form-item>
                    <el-form-item label="主机号" required>
                       <el-input v-model="form.port" placeholder="请输入主机号"/>
                    </el-form-item>
                </div>

                <el-form-item label="邮箱" required>
                   <el-input v-model="form.email" type="email" placeholder="请输入邮箱"/>
                </el-form-item>
                <el-form-item label="抢课码" required>
                   <el-input v-model="form.fuel" placeholder="请输入提供给你的抢课码"/>
                </el-form-item>
            </el-form>
        </div>
        <p>**请确保所填信息完全正确，选课结果将会发送到该邮箱。</p>
        <el-button
            type="primary"
            @click="submitSelected"
            :disabled="!canBeSubmitted || submitting"
        >提交</el-button>
    </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { myMessage } from "@/message.js";
import { bookCourse } from "@/request.js";
import { ElMessageBox } from "element-plus";

const form = ref({
    username: '',
    password: '',
    email: '',
    fuel: '',
    cookie: '',
    port: '',
    loginMethod: '1'
})
const submitting = ref(false)
const expectDelete = ref(null)  // 记录要撤销的课程
const labelPosition = ref('right')

let isMobile = sessionStorage.getItem('isMobile')
if (isMobile && isMobile === '1') {
    labelPosition.value = 'top'
} else {
    labelPosition.value = 'right'
}

let emailRegex = /.+@.+\.com/
const fuelRegex = /^[A-Za-z0-9/+]{67}=$/

// 判断当前输入是否能提交
const canBeSubmitted = computed(() => {
    return form.value.username !== '' &&
        (form.value.password !== '' || form.value.cookie !== '' && form.value.port !== '') &&
        form.value.email !== '' &&
        props.currentSelecting.length > 0 &&
        form.value.fuel !== ''
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
    if (!emailRegex.test(form.value.email)) {
        myMessage('邮箱格式不正确', 'error')
        return
    }
    if (!fuelRegex.test(form.value.fuel)) {
        myMessage('抢课码格式不正确', 'error')
        return
    }
    if (props.currentSelecting.length > 5) {
        myMessage('意向课程总数不能超过5个', 'error')
        return
    }
    await ElMessageBox.confirm('请再次仔细检查当前所有信息是否完全正确，否则可能会影响选课结果噢', '确认要提交嘛？' , {
        confirmButtonText: '确认提交',
        cancelButtonText: '再检查检查',
        type: 'warning'
    }).then(async () => {
        let pathName = location.pathname
        grecaptcha.ready(async () => {
            grecaptcha.execute('6Ldd-UkqAAAAALc2zYyefNF1GtkleLSCsT2DENWm', {action: 'submit'}).then(async token => {
                let data = {
                    username: form.value.username,
                    password: form.value.password,
                    email: form.value.email,
                    courses: props.currentSelecting,
                    fuel: form.value.fuel,
                    course_type: pathName.slice(1),
                    cookie: form.value.cookie,
                    port: form.value.port,
                    token: token
                }
                submitting.value = true
                const response = await bookCourse(data)
                if (response.data.code === 1) {
                    myMessage('预约信息提交成功！', 'success')
                    emits('update:openDrawer', false)
                    emits('update:currentSelecting', [])
                } else if (response.data.code === 2.5) {
                    myMessage('人机验证失败', 'error')
                } else {
                    myMessage(response.data.message, 'error')
                }
                submitting.value = false
            })
        })
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
    width: 95%;
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
