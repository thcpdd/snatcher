<template>
    <div class="table-title"><span>体育课课程信息</span></div>
    <search-bar @search="content => {courseData = content; totalData = content.length}" :course-type="'pe'"></search-bar>
    <el-collapse class="course-box" accordion>
        <el-collapse-item
            v-for="course in courseData"
            :title="course.course_name"
            :name="course.course_id"
        >
            <div style="float: left">课程ID：{{ course.course_id }}</div><br/>
            <div style="float: left">开课年级：{{ course.grade }}</div><br/>
            <el-button
                type="primary"
                style="float: right; margin-bottom: 4px;margin-right: 8px"
                size="small"
                @click="currentSelecting.push(course);myMessage('课程选择成功', 'success')"
            >选择</el-button>
        </el-collapse-item>
    </el-collapse>
    <!-- 翻页 -->
    <paginator @update:current-page="pageChangeHandle" :total-data="totalData"></paginator>
    <!--  打开对话框  -->
    <el-badge :value="currentSelecting.length" type="primary">
        <el-button
            type="primary"
            @click="() => openDrawer = true"
            :disabled="currentSelecting.length === 0"
            title="在表格中勾选你的意向课程"
        >确认</el-button>
    </el-badge>
    <!--  对话框  -->
    <Drawer
        :openDrawer="openDrawer"
        :currentSelecting="currentSelecting"
        @update:openDrawer="() => openDrawer = false"
        @update:currentSelecting="(_new) => currentSelecting = _new"
    />
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Paginator from "@/components/Paginator.vue";
import Drawer from "@/components/Drawer.vue";
import {getPECoursesCount, getPECourses} from "@/request.js";
import SearchBar from "@/components/SearchBar.vue";
import {myMessage} from "@/message.js";


const courseData = ref([])
const currentSelecting = ref([])
const openDrawer = ref(false)
const totalData = ref(1)


onMounted(async () => {
    totalData.value = await getPECoursesCount()
    courseData.value = await getPECourses(1)
})

async function pageChangeHandle(page) {
    // 由于搜索而导致的页码更新不需要再次请求
    if (sessionStorage.getItem('search')) {
        // delete currentSelecting.value  // 清除之前选择的数据
        sessionStorage.removeItem('search')
        return
    }
    courseData.value = await getPECourses(page)
}
</script>