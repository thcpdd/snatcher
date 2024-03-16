<template>
    <div class="table-title"><span>公选课课程信息</span></div>
    <!-- 课程信息表格  -->
    <el-table
        ref="multipleTableRef"
        :data="courseData"
        @selection-change="selectionHandle"
        :stripe="true"
        :row-key="row => row.course_no"
        border
        style="margin-top: 19px; margin-bottom: 20px; width: 97%;"
    >
        <el-table-column type="selection" :reserve-selection="true" width="55" align="center"/>
        <el-table-column type="index" :index="index => index + 1" label="序号" width="70" align="center"/>
        <el-table-column property="courseName" label="课程名" align="center" width="500"></el-table-column>
        <el-table-column property="course_id" label="课程ID" width="700" align="center"/>
        <el-table-column property="course_no" label="课程号" align="center"/>
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
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营1',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0871'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营2',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0872'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0873'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0874'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0875'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0876'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0877'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0878'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a0879'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08799'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08788'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08777'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08766'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08755'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08744'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08733'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08722'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08711'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a08700'
    },
    {
        'courseName': ' Python编程入门和数据可视化项目实战+无人驾驶实训营',
        'course_id': '046AE8EEAA905693E0630284030A6E27',
        'course_no': '5600214a087786'
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

<style>
.table-title {
    font-size: 20px;
    font-weight: bold;
    margin-top: 14px;
}
</style>