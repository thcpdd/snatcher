<template>
    <div class="paginator">
        <el-pagination
            small
            background
            layout="prev, pager, next"
            :total="50"
            class="mt-4"
            :current-page="currentPage"
            @update:current-page="pageChangeHandle"
        />
    </div>
</template>

<script setup>
import {ref, defineEmits} from 'vue'

const currentPage = ref(1)
const changePage = defineEmits(['update:currentPage'])
function pageChangeHandle(page) {
    currentPage.value = page
    changePage('update:currentPage', page)
}
</script>

<style>
.paginator {
    margin-bottom: 15px;
    margin-left: 43%;
}
</style>
