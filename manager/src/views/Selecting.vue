<template>
    <div>
        <h3>选课日志实时监控</h3>
        <div style="margin-bottom: 15px">
            <el-switch
                v-model="monitor"
                active-text="开启监控"
                inactive-text="关闭监控"
                @change="monitorChange"
            />
        </div>
        <el-table
            :data="logs"
            stripe
            border
            table-layout="auto"
            style="width: 95%;margin-bottom: 20px"
        >
            <el-table-column prop="username" label="学号" align="center"/>
            <el-table-column prop="course_name" label="课程名" align="center"/>
            <el-table-column prop="1" label="kch_id" align="center"/>
            <el-table-column prop="2" label="xkkz_id" align="center"/>
            <el-table-column prop="3" label="do_jxb_ids" align="center"/>
            <el-table-column prop="4" label="选课请求" align="center"/>
            <el-table-column prop="error" label="运行时异常" align="center"/>
            <el-table-column prop="retry" label="重试次数" align="center"/>
        </el-table>
    </div>
</template>

<script setup>
import {onBeforeUnmount} from "vue";
import {ref} from "vue";
import {myMessage} from "@/message.js";

const logs = ref([])
const monitor = ref(false)
let ws = null

function monitorChange(value) {
    if (value) {
        let token = localStorage.getItem('token')
        ws = new WebSocket('ws://localhost:8000/manage/monitor?token=' + token)

        ws.onmessage = (event) => {
            let data = JSON.parse(event.data)
            if (data.status === 1) {
                data.msg.forEach(item => {
                    logs.value.push(item)
                })
            } else {
                let message = data.msg
                let username = message['username']
                let course_name = message['course_name']
                let flag = false
                for (let i = 0; i < logs.value.length; i++) {
                    let log = logs.value[i]
                    if (log['username'] === username && log['course_name'] === course_name) {
                        log[message['name']] = message['msg']
                        let m = `${username} - ${course_name}：${message['name']} - ${message['msg']}`
                        myMessage(m, 'warning')
                        flag = true
                        break
                    }
                }
                if (!flag) {
                    let new_log = {username: username, course_name: course_name}
                    new_log[message['name']] = message['msg']
                    logs.value.push(new_log)
                }
            }
        }
    } else {
        ws.close()
    }
}
onBeforeUnmount(() => {
    if (ws) {
        ws.close()
    }
})
</script>
