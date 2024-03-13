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
import {ref} from 'vue'

const currentPage = ref(1)

function pageChangeHandle(page) {
    console.log(page)
    currentPage.value = page
}
</script>