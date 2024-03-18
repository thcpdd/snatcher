import axios from "axios";


export const requests = axios.create({
    baseURL: "http://127.0.0.1:8000/vpn",
})

export async function getPECoursesCount() {
    let localPECount = sessionStorage.getItem('peCount')
    if (!localPECount) {
        await requests.get('/pe/count').then((response) => {
            sessionStorage.setItem('peCount', response.data)
            localPECount = response.data
        })
    }
    return Number(localPECount);
}

export async function getPCCoursesCount() {
    let localPCCount = sessionStorage.getItem('pcCount')
    if (!localPCCount) {
        await requests.get('/pc/count').then((response) => {
            sessionStorage.setItem('pcCount', response.data)
            localPCCount = response.data
        })
    }
    return Number(localPCCount);
}

export async function getPECourses(page) {
    let localPECourses = sessionStorage.getItem(`peCourses_${page}`)
    if (!localPECourses) {
        await requests.get(`/pe/${page}`).then((response) => {
            sessionStorage.setItem(`peCourses_${page}`, JSON.stringify(response.data))
            localPECourses = response.data
        })
    } else {
        localPECourses = JSON.parse(localPECourses)
    }
    return localPECourses;
}

export async function getPCCourses(page) {
    let localPCCourses = sessionStorage.getItem(`pcCourses_${page}`)
    if (!localPCCourses) {
        await requests.get(`/pc/${page}`).then((response) => {
            sessionStorage.setItem(`pcCourses_${page}`, JSON.stringify(response.data))
            localPCCourses = response.data
        })
    } else {
        localPCCourses = JSON.parse(localPCCourses)
    }
    return localPCCourses;
}

export async function searchCourse(courseType, searchContent) {
    let searchResult = []
    if (courseType === 'pe') {
        await requests.get(`/pe/?keyword=${searchContent}`).then(response => {
            searchResult = response.data
        })
    } else {
        await requests.get(`/pc/?keyword=${searchContent}`).then(response => {
            searchResult = response.data
        })
    }
    return searchResult
}

export function submitCourse(pathName, data) {
    requests.post(pathName, data).then(response => {
        console.log(response.data)
    })
}
