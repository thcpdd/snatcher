import axios from "axios";


const requests = axios.create({
    baseURL: 'http://127.0.0.1:8000/manage'
})

requests.interceptors.request.use((config) => {
    let token = localStorage.getItem('token')
    if (token) {
        config.headers['Authorization'] = token
    }
    return config
})
requests.interceptors.response.use((response) => {
    if (location.pathname === '/login' && response.data.success) {
        localStorage.setItem('token', response.headers['authorization'])
    }
    return response
}, (error) => {
    if (error.response.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
    }
    return Promise.reject(error)
})


export async function getAllSelectedData(page) {
    return await requests.get(`/selected/${page}`).then((response) => {
        return response.data
    })
}

export async function getAllSelectedCount() {
    return await requests.get(`/selected/count`).then((response) => {
        return response.data
    })
}

export async function getFailedData(page) {
    return await requests.get(`/failed/${page}`).then((response) => {
        return response.data
    })
}

export async function getFailedCount() {
    return await requests.get('/failed/count').then((response) => {
        return response.data
    })
}

export async function getVerifyCodes(page) {
    return await requests.get(`/codes/${page}`).then((response) => {
        return response.data
    })
}

export async function getVerifyCount() {
    return await requests.get('/codes/count').then((response) => {
        return response.data
    })
}

export async function generateVerifyCode(username) {
    return await requests.post(`/codes?username=${username}`).then((response) => {
        return response.data
    })
}

export async function login(username, password) {
    return await requests.post('/login', {username: username, password: password}).then((response) => {
        return response.data
    })
}

export async function getPECoursesCount() {
    let localPECount = 0
    await requests.get('/pe/count').then((response) => {
        localPECount = response.data
    })
    return Number(localPECount);
}

export async function getPCCoursesCount() {
    let localPCCount = 0
    await requests.get('/pc/count').then((response) => {
        localPCCount = response.data
    })
    return Number(localPCCount);
}

export async function getPECourses(page) {
    let localPECourses = []
    await requests.get(`/pe/${page}`).then((response) => {
        localPECourses = response.data
    })
    return localPECourses;
}

export async function getPCCourses(page) {
    let localPCCourses = []
    await requests.get(`/pc/${page}`).then((response) => {
        localPCCourses = response.data
    })
    return localPCCourses;
}
