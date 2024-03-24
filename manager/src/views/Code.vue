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
            <el-table-column prop="id" label="序号" align="center"/>
            <el-table-column prop="username" label="学号" align="center"/>
            <el-table-column prop="verify_code" label="抢课码" align="center"/>
            <el-table-column prop="is_used" label="是否使用" align="center"/>
            <el-table-column prop="create_at" label="创建时间" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
        <el-dialog v-model="open" align-center title="生成唯一抢课码" style="text-align: left; width: 350px">
            <el-input placeholder="请输入学号" v-model="username"></el-input>
            <el-button
                type="primary"
                style="margin-top: 10px; width: 100%"
                :disabled="!username"
                @click="createVerifyCode"
            >生成</el-button>
        </el-dialog>
    </div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import Paginator from "@/components/Paginator.vue";
import {generateVerifyCode, getVerifyCodes, getVerifyCount} from "@/request.js";
import {ElMessageBox} from 'element-plus'

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])
const open = ref(false)
const username = ref('')

onMounted(async () => {
    total.value = await getVerifyCount()
    currentData.value = await getVerifyCodes(1)
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    currentData.value = await getVerifyCodes(page)
}
const createVerifyCode = async () => {
    let verifyCode = await generateVerifyCode(username.value)
    await ElMessageBox.alert(verifyCode, '这是你的抢课码，请妥善保存。', {
        confirmButtonText: '确定',
        type: 'success'
    }).then(() => {
        location.reload()
    })
}
</script>