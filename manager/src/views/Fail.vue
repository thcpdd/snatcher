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
            <el-table-column prop="id" label="序号" width="60" align="center"/>
            <el-table-column prop="username" label="学号" width="120" align="center"/>
            <el-table-column prop="port" label="端口" width="53" align="center"/>
            <el-table-column prop="course_name" label="课程名" width="380" align="center"/>
            <el-table-column prop="created_at" label="创建时间" width="167" align="center"/>
            <el-table-column prop="log_key" label="日志key" width="410" align="center"/>
            <el-table-column prop="failed_reason" label="失败原因" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>
<script setup>
import {ref, onMounted} from "vue";
import Paginator from "@/components/Paginator.vue";
import {getFailedData, getFailedCount} from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    total.value = await getFailedCount()
    currentData.value = await getFailedData(1)
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    currentData.value = await getFailedData(page)
}
</script>