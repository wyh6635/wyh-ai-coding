import request from './request'

export const getStudents = (params) => request.get('/students', { params })
export const getStudent = (id) => request.get(`/students/${id}`)
export const createStudent = (data) => request.post('/students', data)
export const updateStudent = (id, data) => request.put(`/students/${id}`, data)
export const deleteStudent = (id) => request.delete(`/students/${id}`)

export const getSubjects = (params) => request.get('/subjects', { params })
export const getAllSubjects = () => request.get('/subjects/all')
export const getSubject = (id) => request.get(`/subjects/${id}`)
export const createSubject = (data) => request.post('/subjects', data)
export const updateSubject = (id, data) => request.put(`/subjects/${id}`, data)
export const deleteSubject = (id) => request.delete(`/subjects/${id}`)

export const getScores = (params) => request.get('/scores', { params })
export const getScore = (id) => request.get(`/scores/${id}`)
export const createScore = (data) => request.post('/scores', data)
export const batchCreateScores = (data) => request.post('/scores/batch', data)
export const updateScore = (id, data) => request.put(`/scores/${id}`, data)
export const deleteScore = (id) => request.delete(`/scores/${id}`)
export const getScoreStats = () => request.get('/scores/stats/summary')

export const getDashboardStats = () => request.get('/dashboard/stats')
export const getSubjectScores = () => request.get('/dashboard/subject-scores')
export const getRecentStudents = (limit = 5) => request.get('/dashboard/recent-students', { params: { limit } })
export const getRecentScores = (limit = 5) => request.get('/dashboard/recent-scores', { params: { limit } })
export const getExamTypes = () => request.get('/dashboard/exam-types')
export const getCategories = () => request.get('/dashboard/categories')
export const getClassNames = () => request.get('/dashboard/class-names')

export const changePassword = (data) => request.post('/users/change-password', data)

export const getProfile = () => request.get('/users/profile')
export const updateProfile = (data) => request.put('/users/profile', data)