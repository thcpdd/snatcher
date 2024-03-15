<template>
    <div class="table-title"><span>公选课课程信息</span></div>
    <el-table
        ref="multipleTableRef"
        :data="courseData"
        @selection-change="selectionHandle"
        :stripe="true"
        :row-key="getRowKey"
        border
        style="margin-top: 19px; margin-bottom: 20px; width: 97%;"
    >
        <el-table-column type="selection" :reserve-selection="true" width="55" align="center"/>
        <el-table-column type="index" :index="index => index + 1" label="序号" width="70" align="center"/>
        <el-table-column property="courseName" label="课程名" align="center" width="500"></el-table-column>
        <el-table-column property="course_id" label="课程ID" width="700" align="center"/>
        <el-table-column property="course_no" label="课程号" align="center"/>
    </el-table>
    <paginator @update:current-page="pageChangeHandle"></paginator>
    <el-button type="primary" @click="() => canBeSubmitted = true">确认</el-button>
    <!--  对话框  -->
    <el-drawer v-model="canBeSubmitted" title="提交你的选课信息" direction="ttb" size="50%">
        <div class="dialog">
            <span style="font-weight: bolder">你的意向课程：</span>
            <p v-for="data in currentSelected">{{ data.courseName }}</p>
        </div>
        <h3>为了您更好的体验，我们需要收集你的一些信息。</h3>
        <div class="user-info">
            学号：<el-input v-model="username" style="width: 240px" placeholder="请输入你的学号"/>
        </div>
        <div class="user-info">
            密码：<el-input v-model="password" style="width: 240px" type="password" placeholder="请输入你的密码"/>
        </div>
        <div class="user-info">
            邮箱：<el-input v-model="email" style="width: 240px" placeholder="请输入你的邮箱" />
        </div>
        <el-button type="primary" @click="submitSelected">提交</el-button>
    </el-drawer>
</template>

<script setup>
import {ref} from 'vue'
import Paginator from "@/components/Paginator.vue";

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
const canBeSubmitted = ref(false)
const courseData = ref(allData.slice(0, 10))
const currentSelected = ref([])
const username = ref('')
const password = ref('')
const email = ref('')

function getRowKey(row) {
    return row.course_no
}

function selectionHandle(row) {
    currentSelected.value = row
}

function pageChangeHandle(page) {
    courseData.value = allData.slice((page - 1) * 10, page * 10)
}

function submitSelected() {
    alert(username.value)
    alert(password.value)
    alert(email.value)
}
</script>

<style>
.table-title {
    font-size: 20px;
    font-weight: bold;
    margin-top: 14px;
}
.dialog {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    background-color: aliceblue;
    padding-top: 17px;
    padding-bottom: 8px;
}
.user-info {
    margin-bottom: 10px;
}
</style>