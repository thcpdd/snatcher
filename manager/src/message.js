import { ElMessage } from 'element-plus'


export function myMessage(message, type) {
    ElMessage({
        message: message,
        type: type,
        showClose: true
    })
}