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
    if (location.pathname === '/login' && response.data.code === 1) {
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


export function getAllSelectedData(page) {
    return requests.get(`/submitted/${page}`)
}

export function getFailedData(page) {
    return requests.get(`/failure/${page}`)
}

export function getFuel(page) {
    return requests.get(`/energy/${page}`)
}

export function generateFuel(username) {
    return requests.post('/fuel', {username: username})
}

export function login(username, password) {
    return requests.post('/login', {username: username, password: password})
}

export function getPECourses(page) {
    return requests.get(`/pe/${page}`)
}

export function getPCCourses(page) {
    return requests.get(`/pc/${page}`)
}
