<template>
    <div class="table-title"><span>体育课课程信息</span></div>
    <el-table
        ref="multipleTableRef"
        :data="courseData"
        @selection-change="selectionHandle"
        :row-key="row => row.courseID"
        :stripe="true"
        border
        style="margin-top: 19px; margin-bottom: 20px; width: 97%;"
    >
        <el-table-column type="selection" :reserve-selection="true" width="55" align="center"/>
        <el-table-column type="index" :index="index => index + 1" label="序号" width="70" align="center"/>
        <el-table-column property="courseName" label="课程名" align="center" width="500"></el-table-column>
        <el-table-column property="courseID" label="课程ID" width="700" align="center"/>
        <el-table-column property="grade" label="开课年级" align="center"/>
    </el-table>
    <!-- 翻页 -->
    <paginator @update:current-page="pageChangeHandle"></paginator>
    <!--  打开对话框  -->
    <el-button
        type="primary"
        @click="() => openDrawer = true"
        :disabled="currentSelecting.length === 0"
        title="在表格中勾选你的意向课程"
    >确认</el-button>
    <!--  对话框  -->
    <Drawer
        :openDrawer="openDrawer"
        :currentSelecting="currentSelecting"
        @update:openDrawer="() => openDrawer = false"
    />
</template>

<script setup>
import {ref} from 'vue'
import Paginator from "@/components/Paginator.vue";
import Drawer from "@/components/Drawer.vue";

const allData = [
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0511',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0512',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0513',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0514',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0515',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0516',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0517',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0518',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0519',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05199',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05111',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05122',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05133',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05144',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05155',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05166',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05177',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05188',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y05199',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y0519977',
        'grade': '2022'
    },
]
const courseData = ref(allData.slice(0, 10))
const currentSelecting = ref([])
const openDrawer = ref(false)

function selectionHandle(row) {
    currentSelecting.value = row
}

function pageChangeHandle(page) {
    courseData.value = allData.slice((page - 1) * 10, page * 10)
}
</script>