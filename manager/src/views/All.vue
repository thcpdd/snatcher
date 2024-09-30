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
            <el-table-column prop="row_id" label="序号" width="230" align="center"/>
            <el-table-column prop="username" label="学号" width="110" align="center"/>
            <el-table-column prop="email" label="邮箱" align="center"/>
            <el-table-column prop="course_name" label="课程名" width="420" align="center"/>
            <el-table-column prop="updated_at" label="更新时间" width="200" align="center"/>
            <el-table-column prop="log_key" label="日志key" width="520" align="center"/>
            <el-table-column prop="success" label="是否成功" width="100" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Paginator from "@/components/Paginator.vue";
import { getAllSelectedData } from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    const response = await getAllSelectedData(1)
    currentData.value = response.data.data['results']
    total.value = Number(response.data.data['total'])
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    const response = await getAllSelectedData(page)
    currentData.value = response.data.data['results']
}
</script>
