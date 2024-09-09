import axios from "axios";
import NProgress from 'nprogress'


export const requests = axios.create({
    baseURL: "http://127.0.0.1:8000/vpn",  // 本地环境需要写上详细的URL，生产环境不用写。
})

requests.interceptors.request.use(config => {
    NProgress.start()
    return config
}, error => {
    NProgress.done()
    return Promise.reject(error)
})

requests.interceptors.response.use(response => {
    NProgress.done()
    return response
}, error => {
    NProgress.done()
    return Promise.reject(error)
})


export function getPECourses(page) {
    return requests.get(`/pe/${page}`)
}

export function getPCCourses(page) {
    return requests.get(`/pc/${page}`)
}

export async function searchCourse(courseType, searchContent) {
    let searchResult = []
    if (courseType === 'pe') {
        await requests.get('/pe', {params: {keyword: searchContent}}).then(response => {
            searchResult = response.data.data['results']
        })
    } else {
        await requests.get('/pc', {params: {keyword: searchContent}}).then(response => {
            searchResult = response.data.data['results']
        })
    }
    return searchResult
}

export function bookCourse(data) {
    return requests.post('/book', data)
}

export function searchProgress(fuel) {
    return requests.get('/user/progress', {params: {fuel: fuel}})
}

export function querySelectedNumber(course_type) {
    return requests.get('/selection', {params: {course_type: course_type}})
}

export function querySystemOpeningTime() {
    return requests.get('/system/opening-time')
}
