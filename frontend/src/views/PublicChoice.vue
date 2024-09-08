<template>
    <div class="table-title"><span>公选课课程信息</span></div>
    <opening-time/>
    <!-- 课程信息表格  -->
    <search-bar @search="content => {courseData = content; totalData = content.length}" :course-type="'pc'"></search-bar>
    <el-collapse class="course-box" accordion>
        <el-collapse-item
            v-for="course in courseData"
            :title="course.course_name"
            :name="course['jxb_id']"
        >
            <div style="float: left">课程ID：{{ course['course_id'] }}</div><br/>
            <div style="float: left">教学班名称：{{ course['jxbmc'] }}</div><br/>
            <selected-number-listener
                :selected-number="stock[course['jxb_id']]"
                :update-timestamp="stock['updated_at']"
            ></selected-number-listener>
            <el-button
                type="primary"
                style="float: right; margin-bottom: 4px;margin-right: 8px"
                size="small"
                @click="currentSelecting.push(course);myMessage('添加课程成功，请继续选择其他课程 或 点击下方的确认按钮', 'success')"
            >添加</el-button>
        </el-collapse-item>
    </el-collapse>
    <!-- 翻页 -->
    <paginator @update:current-page="pageChangeHandle" :total-data="totalData"></paginator>
    <!--  打开对话框  -->
    <el-badge :value="currentSelecting.length" type="primary">
        <el-button
            type="primary"
            @click="openDrawer = true"
            :disabled="currentSelecting.length === 0"
            title="在表格中选择你的意向课程"
            style="margin-bottom: 13px;"
        >确认</el-button>
    </el-badge>
    <!--  对话框  -->
    <Drawer
        :openDrawer="openDrawer"
        :currentSelecting="currentSelecting"
        @update:currentSelecting="(_new) => currentSelecting = _new"
        @update:openDrawer="() => openDrawer = false"
    />
</template>

<script setup>
import { ref, onMounted, inject, onBeforeUnmount } from 'vue'
import Paginator from "@/components/Paginator.vue";
import Drawer from "@/components/Drawer.vue";
import SearchBar from "@/components/SearchBar.vue";
import { myMessage } from "@/message.js";
import { getPCCourses, querySelectedNumber } from "@/request.js";
import SelectedNumberListener from "@/components/SelectedNumberListener.vue";
import OpeningTime from "@/components/OpeningTime.vue"

const courseData = ref([])
const currentSelecting = ref([])
const openDrawer = ref(false)
const totalData = ref(1)
const stock = ref({})
let timer

const listener = async () => {
    const response = await querySelectedNumber('10')
    stock.value = response.data.data
}

const updateCourseData = async (page) => {
    let localPCCourses = sessionStorage.getItem(`pcCourses_${page}`)
    if (localPCCourses) {
        let localPECount = sessionStorage.getItem('pcCount')
        totalData.value = Number(localPECount)
        courseData.value = JSON.parse(localPCCourses)
    } else {
        const response = await getPCCourses(page)
        totalData.value = response.data.data['total']
        courseData.value = response.data.data['results']
        sessionStorage.setItem(`pcCourses_${page}`, JSON.stringify(courseData.value))
        sessionStorage.setItem(`pcCount`, JSON.stringify(totalData.value))
    }
}

onMounted(async () => {
    const prepare = inject('prepare')
    await prepare()
    await updateCourseData(1)
    await listener()
    timer = setInterval(listener, 1000 * 60 * 5)  // 5 minutes
})

async function pageChangeHandle(page) {
    // 由于搜索而导致的页码更新不需要再次请求
    if (sessionStorage.getItem('search')) {
        sessionStorage.removeItem('search')
        return
    }
    await updateCourseData(page)
}

onBeforeUnmount(() => {
    clearInterval(timer)
})

</script>

<style>
.table-title {
    font-size: 20px;
    font-weight: bold;
    margin-top: 14px;
}
.course-box {
    width: 95%;
    margin-top: 15px;
    margin-bottom: 15px;
    overflow: hidden;
    white-space: nowrap;
}
</style>