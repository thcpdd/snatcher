<template>
    <div class="form-content">
        <div class="inner-content">
            <!--            <el-form-->
            <!--                ref="ruleFormRef"-->
            <!--                style="max-width: 250px; margin-top: 20px"-->
            <!--                :model="data"-->
            <!--                status-icon-->
            <!--                label-width="auto"-->
            <!--                class="demo-ruleForm"-->
            <!--            >-->
            <!--                <el-form-item label="学号" prop="pass">-->
            <!--                    <el-input v-model="data.username" type="text"/>-->
            <!--                </el-form-item>-->
            <!--                <el-form-item label="密码" prop="checkPass">-->
            <!--                    <el-input v-model="data.password" type="password"/>-->
            <!--                </el-form-item>-->
            <!--                <el-form-item label="邮箱" prop="age">-->
            <!--                    <el-input v-model="data.email"/>-->
            <!--                </el-form-item>-->
            <!--                <el-form-item>-->
            <!--                    <el-button type="primary" @click="">提交</el-button>-->
            <!--                    <el-button @click="">重置</el-button>-->
            <!--                </el-form-item>-->
            <!--            </el-form>-->
            <el-table
                ref="multipleTableRef"
                :data="courseData"
                :table-layout="layout"
                @selection-change=""
                :stripe="true"
                border
                style="margin-top: 20px; margin-bottom: 50px; width: 98%;"
            >
                <el-table-column type="selection" width="55" align="center"/>
                <el-table-column type="index" :index="indexMethod" label="序号" width="90" align="center"/>
                <el-table-column property="courseName" label="课程名" align="center" width="500"></el-table-column>
                <el-table-column property="course_id" label="课程ID" width="450" align="center"/>
                <el-table-column property="course_no" label="课程号" align="center"/>
            </el-table>
        </div>
    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'

// const data = reactive({
//     'username': '',
//     'password': '',
//     'email': '',
// })
const layout = ref('fixed');

function indexMethod(index) {
    return index + 1
}

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

</script>

<style>
</style>