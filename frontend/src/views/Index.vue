<template>
    <div id="page1"></div>
    <div class="index-content">
        <div class="t1">
            <span class="t1-font">
                Snatcher<br/>基于延时任务队列的
            </span>
        </div>
        <div class="t2"><span class="t2-font">Python Spider Program</span></div>
        <div class="t3"><span>选择课程-填写相关信息-提交-预约抢课成功</span></div>
        <div style="margin-top: 3%">
            <el-button type="primary"
                       style="width: max-content;font-weight: bolder"
                       @click="router.push('/pc')"
                       size="large"
                       class="to-book"
            >开始预约抢课</el-button>
        </div>
    </div>
</template>

<script setup>
import router from "@/router/index.js";
import { onMounted } from "vue";

let width = window.innerWidth;
function setFontSize(selector, rate) {
    document.querySelector(selector).style.fontSize = width / rate + "px";
}
onMounted(async () => {
    // 重新调整移动端的字体大小
    if (sessionStorage.getItem("isMobile")) {
        setFontSize(".t1-font", 10);
        setFontSize(".t2-font", 17);
        setFontSize(".t3", 27);
        let node = document.getElementsByClassName('index-content')[0]
        node.style.lineHeight = '47px'
        node = document.querySelector('.to-book')
        node.style.height = '32px'
    }
})
</script>

<style>
@font-face {
    font-family: "fangzhen";  /* font-spider */
    src: url("/fzyihei.ttf");
}
@font-face {
    font-family: "SUB";
    src: url("/Segoe UI Black.ttf");
}
.index-content {
    background: linear-gradient(0deg, #d3f2fa 20%, #c4cefa);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    flex-direction: column;
}
.t1 {
    margin-top: 5%;
}
.t1-font {
    font-size: 500%;
    background: linear-gradient(315deg, #4760ff 50%,#66e7fc);
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: "fangzhen", monospace;
}
.t2 {
    margin-top: 1%;
}
.t2-font {
    font-size: 300%;
    font-weight: bold;
    font-family: "SUB", monospace;
    color: #2a2929;
}
.t3 {
    margin-top: 2%;
    font-size: 150%;
    font-weight: bold;
}
</style>
