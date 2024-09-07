<template>
    <div>
        <h3>体育课课程信息</h3>
        <el-table
            :data="currentData"
            stripe
            border
            table-layout="auto"
            style="width: 95%"
        >
            <el-table-column prop="row_id" label="序号" align="center"/>
            <el-table-column prop="course_name" label="课程名" align="center"/>
            <el-table-column prop="course_id" label="课程ID" align="center"/>
            <el-table-column prop="grade" label="年级" align="center"/>
            <el-table-column prop="study_year" label="选课学年" align="center"/>
            <el-table-column prop="term" label="学期" align="center"/>
            <el-table-column prop="jxb_id" label="教学班ID" align="center"/>
            <el-table-column prop="jxbmc" label="教学班名称" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import Paginator from "@/components/Paginator.vue";
import { getPECourses } from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    const response = await getPECourses(1)
    currentData.value = response.data.data['results']
    total.value = Number(response.data.data['total'])
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    const response = await getPECourses(page)
    currentData.value = response.data.data['results']
}
</script>