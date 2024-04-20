<template>
    <div>
        <h3>公选课课程信息</h3>
        <el-table
            :data="currentData"
            stripe
            border
            table-layout="auto"
            style="width: 95%"
        >
            <el-table-column prop="id" label="序号" align="center"/>
            <el-table-column prop="course_name" label="课程名" align="center"/>
            <el-table-column prop="course_id" label="课程ID" align="center"/>
            <el-table-column prop="course_no" label="课程号" align="center"/>
            <el-table-column prop="study_year" label="选课学年" align="center"/>
            <el-table-column prop="term" label="学期" align="center"/>
            <el-table-column prop="period" label="学期阶段" align="center"/>
        </el-table>
        <paginator :total-data="total" @update:current-page="pageChangeHandle"></paginator>
    </div>
</template>
<script setup>
import {ref, onMounted} from "vue";
import Paginator from "@/components/Paginator.vue";
import {getPCCourses, getPCCoursesCount} from "@/request.js";

const total = ref(0)
const currentPage = ref(1)
const currentData = ref([])

onMounted(async () => {
    total.value = await getPCCoursesCount()
    currentData.value = await getPCCourses(1)
})

const pageChangeHandle = async (page) => {
    currentPage.value = page
    currentData.value = await getPCCourses(page)
}
</script>