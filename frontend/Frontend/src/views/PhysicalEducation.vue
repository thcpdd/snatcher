<template>
    <div class="pc-title"><span>体育课课程信息</span></div>
    <el-table
        ref="multipleTableRef"
        :data="courseData"
        @selection-change="selectionHandle"
        :stripe="true"
        border
        style="margin-top: 19px; margin-bottom: 20px; width: 99%;"
    >
        <el-table-column type="selection" width="55" align="center"/>
        <el-table-column type="index" :index="indexMethod" label="序号" width="70" align="center"/>
        <el-table-column property="courseName" label="课程名" align="center" width="500"></el-table-column>
        <el-table-column property="courseID" label="课程ID" width="700" align="center"/>
        <el-table-column property="grade" label="开课年级" align="center"/>
    </el-table>
    <paginator></paginator>
</template>

<script setup>
import Paginator from "@/components/Paginator.vue";

const courseData = [
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    }, {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
    {
        'courseName': '大学体育之体育舞蹈俱乐部2',
        'courseID': '1000Y31Y051',
        'grade': '2022'
    },
]

function indexMethod(index) {
    return index + 1
}

function selectionHandle(row) {
    row.forEach(data => {
        console.log(data.courseName)
    })
}
</script>