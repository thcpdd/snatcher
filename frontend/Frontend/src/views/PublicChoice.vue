<template>
    <div class="pc-title"><span>公选课课程信息</span></div>
    <div>当前已选择：{{ current_selected }}</div>
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
        <el-table-column property="course_id" label="课程ID" width="700" align="center"/>
        <el-table-column property="course_no" label="课程号" align="center"/>
    </el-table>
    <paginator></paginator>
</template>

<script setup>
import {ref} from 'vue'
import Paginator from "@/components/Paginator.vue";

const courseData = [
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087'
    },
]

const current_selected = ref([])

function indexMethod(index) {
    return index + 1
}

function selectionHandle(row) {
    row.forEach(data => {
        current_selected.value.push(data.courseName)
    })
}
</script>

<style>
.pc-title {
    font-size: 20px;
    font-weight: bold;
    margin-top: 14px;
}
</style>