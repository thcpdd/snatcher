<template>
    <div class="search-bar">
        <el-input v-model="searchContent" style="width: 60%" placeholder="输入课程名搜索" />
        <el-button
            type="primary"
            :disabled="searchContent === ''"
            style="margin-left: 5px"
            @click="searchHandle"
        >搜索</el-button>
    </div>
</template>

<script setup>
import {ref, defineEmits, defineProps} from "vue";
import {searchCourse} from "@/request.js";

const searchContent = ref('')
const searchWasCalled = defineEmits(['search'])
const props = defineProps({
    courseType: String
})

async function searchHandle() {
    sessionStorage.setItem('search', '1')
    searchWasCalled('search', await searchCourse(props.courseType, searchContent.value))
}
</script>

<style>
.search-bar {
    margin-top: 10px;
}
</style>
