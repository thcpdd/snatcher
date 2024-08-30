<template>
    <div>
        <h3>所有抢课码信息</h3>
        <el-button
            type="primary"
            style="margin-bottom: 15px"
            @click="open = true"
        >生成抢课码</el-button>
        <el-table
            :data="currentData"
            stripe
            border
            table-layout="auto"
            style="width: 95%"
        >
            <el-table-column prop="row_id" label="序号" align="center"/>
            <el-table-column prop="username" label="学号" align="center"/>
            <el-table-column prop="fuel" label="抢课码" align="center"/>
            <el-table-column prop="status" label="状态" align="center"/>
            <el-table-column prop="created_at" label="创建时间" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
        <el-dialog v-model="open" align-center title="生成唯一抢课码" style="text-align: left; width: 350px">
            <el-input placeholder="请输入学号" v-model="username"></el-input>
            <el-button
                type="primary"
                style="margin-top: 10px; width: 100%"
                :disabled="!username"
                @click="createFuel"
            >生成</el-button>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Paginator from "@/components/Paginator.vue";
import { generateFuel, getFuel } from "@/request.js";
import { ElMessageBox } from 'element-plus'

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])
const open = ref(false)
const username = ref('')

onMounted(async () => {
    const response = await getFuel(1)
    total.value = Number(response.data.data['total'])
    currentData.value = response.data.data['results']
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    const response = await getFuel(page)
    currentData.value = response.data.data['results']
}

const createFuel = async () => {
    let response = await generateFuel(username.value)
    let fuel = response.data.data['fuel']
    await ElMessageBox.alert(fuel, '这是你的抢课码，请妥善保存。', {
        confirmButtonText: '确定',
        type: 'success'
    }).then(() => {
        location.reload()
    })
}
</script>

<style>
.el-message-box__message {
    overflow: auto;
}
</style>