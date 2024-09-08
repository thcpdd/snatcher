<template>
    <h4>系统开放时间：{{ openingTime }}</h4>
</template>

<script setup>
import { ref } from "vue";
import { querySystemOpeningTime } from "@/request.js";

const openingTime = ref('')
const promise = querySystemOpeningTime()
promise.then((response) => {
    openingTime.value = response.data.data['opening_time']
})
</script>