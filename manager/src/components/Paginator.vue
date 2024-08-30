<template>
    <div class="paginator">
        <el-pagination
            small
            background
            layout="prev, pager, next"
            :page-size="20"
            :total="totalData"
            class="mt-4"
            :current-page="currentPage"
            @update:current-page="pageChangeHandle"
        />
    </div>
</template>

<script setup>
import { ref } from 'vue'

const currentPage = ref(1)
const changePage = defineEmits(['update:currentPage'])


defineProps({
    totalData: Number
})

function pageChangeHandle(page) {
    currentPage.value = page
    changePage('update:currentPage', page)
}
</script>

<style>
.paginator {
    margin-top: 10px;
    margin-bottom: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
