<template>
    <div style="float: left;display: inline-block">
        <span>已选择人数：<b>{{ props.selectedNumber || 0 }}</b></span>
        <el-tooltip
            :content="tooltipContent + updateAt"
            effect="light"
            :placement="tooltipPlacement"
            raw-content
        >
            <el-button
                    size="small"
                    circle style="margin-left: 6px;width: 16px;height: 16px;margin-top: -3px"
                    type="warning"
            >?
            </el-button>
        </el-tooltip>
    </div>
    <br/>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
    selectedNumber: Number,
    updateTimestamp: String,
})
const tooltipContent = "数据来源于教务系统且<b>仅供参考</b>，最后一次更新于："
let tooltipPlacement

const updateAt = computed(() => {
    let content
    if (props.updateTimestamp === undefined) {
        content = '系统暂未开始同步'
    } else {
        const date = new Date()
        date.setTime(Number(props.updateTimestamp) * 1000)
        content = date.toLocaleString()  // timestamp => datetime
    }
    return `<b>${content}</b>`
})

let isMobile = sessionStorage.getItem('isMobile')
if (isMobile && isMobile === '1') {
    tooltipPlacement = 'bottom'
} else {
    tooltipPlacement = 'right'
}

</script>