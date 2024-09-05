<template>
    <div class="table-title"><span>选课进度查询（测试版）</span></div>
    <div class="search-bar">
        <el-input v-model="fuel" style="width: 60%" type="password" placeholder="输入抢课码搜索"/>
        <el-button
            type="primary"
            :disabled="fuel === ''"
            style="margin-left: 5px"
            @click="searchHandle"
        >搜索</el-button>
    </div>
    <div v-if="goals.length === 0">
        <el-empty description="在上方搜索栏中搜索以显示选课进度"/>
    </div>
    <div v-else class="progress-content">
        <div class="progress-detail">
            <div class="description">
                <span>学号
                    <span style="font-weight: bold">{{ username }}</span>
                    ，根据抢课码查询到的选课进度如下（蓝色表示已完成，黑色表示正在进行）：</span>
            </div>
            <el-collapse class="course-box" accordion>
                <el-collapse-item
                    v-for="(_, index) in goals"
                    :title="goals[index]"
                >
                    <el-steps
                        :active="progress[index][0]"
                        align-center
                        style="margin-bottom: 40px"
                    >
                        <el-step title="初始化请求" description="表示系统已经开始选课"/>
                        <el-step title="关键步骤1" description="系统正在获取请求参数1"/>
                        <el-step title="关键步骤2" description="系统正在获取请求参数2"/>
                        <el-step title="选课请求" description="成功即表示选课成功"/>
                    </el-steps>
                    <span style="font-weight: bold;font-size: medium">尝试次数：{{ progress[index][1] }}</span>
                </el-collapse-item>
            </el-collapse>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { myMessage } from "@/message.js";
import { searchProgress } from "@/request.js";
import { ElMessageBox } from "element-plus";

const fuel = ref('')
const username = ref('')
const goals = ref([])
const progress = ref([])

const searchHandle = async () => {
    const fuelRegex = /^[A-Za-z0-9/+]{67}=$/
    if (!fuel.value || !fuelRegex.test(fuel.value)) {
        myMessage('抢课码错误', 'error')
        return null
    }
    const response = await searchProgress(fuel.value)
    const data = response.data.data
    username.value = data.username
    goals.value = data.goals
    if (goals.value.length === 0) {
        await ElMessageBox.alert('请确保你的抢课码是正确的，并且只有当选课开始时才会产生选课进度', '未查询到相关信息' , {
            confirmButtonText: '确认',
            type: 'warning'
        })
        return null
    }
    progress.value = data.progress
}

</script>

<style>
.progress-content {
    margin-top: 40px;
}
.progress-detail {
    margin-top: 20px;
}
</style>