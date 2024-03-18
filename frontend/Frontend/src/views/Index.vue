<template>
    <div>
        首页
        <el-button @click="activeName.push(1)"></el-button>
    </div>
</template>

<script setup>
import {ref, watch} from "vue";

const activeName = ref([])
watch(activeName, () => {
    alert(1)
}, {deep: true})
</script>