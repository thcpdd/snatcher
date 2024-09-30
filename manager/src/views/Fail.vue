<template>
    <div>
        <h3>选课失败的信息</h3>
        <el-table
            :data="currentData"
            stripe
            border
            table-layout="fixed"
            style="width: 95%"
        >
            <el-table-column prop="row_id" label="序号" width="230" align="center"/>
            <el-table-column prop="username" label="学号" width="110" align="center"/>
            <el-table-column prop="port" label="端口" width="53" align="center"/>
            <el-table-column prop="course_name" label="课程名" width="380" align="center"/>
            <el-table-column prop="created_at" label="创建时间" width="167" align="center"/>
            <el-table-column prop="log_key" label="日志key" width="500" align="center"/>
            <el-table-column prop="reason" label="失败原因" width="500" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>
<script setup>
import {ref, onMounted} from "vue";
import Paginator from "@/components/Paginator.vue";
import { getFailedData } from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    let response = await getFailedData(1)
    currentData.value = response.data.data['results']
    total.value = Number(response.data.data['total'])
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    let response = await getFailedData(page)
    currentData.value = response.data.data['results']
}
</script>