<template>
    <div>
        <h3>所有已选课程信息</h3>
        <el-table
            :data="currentData"
            stripe
            border
            table-layout="auto"
            style="width: 95%"
        >
            <el-table-column prop="id" label="序号" align="center"/>
            <el-table-column prop="username" label="学号" align="center"/>
            <el-table-column prop="email" label="邮箱" align="center"/>
            <el-table-column prop="course_name" label="课程名" align="center"/>
            <el-table-column prop="updated_at" label="更新时间" align="center"/>
            <el-table-column prop="log_key" label="日志key" align="center"/>
            <el-table-column prop="success" label="是否成功" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import Paginator from "@/components/Paginator.vue";
import {getAllSelectedData, getAllSelectedCount} from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    total.value = await getAllSelectedCount()
    currentData.value = await getAllSelectedData(1)
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    currentData.value = await getAllSelectedData(page)
}
</script>
