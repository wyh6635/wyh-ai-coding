import request from './request'

export const getCaptcha = () => {
  return request.get('/auth/captcha')
}

export const login = (data) => {
  return request.post('/auth/login', data)
}

export const logout = () => {
  return request.post('/auth/logout')
}

export const getUserInfo = () => {
  return request.get('/auth/user-info')
}