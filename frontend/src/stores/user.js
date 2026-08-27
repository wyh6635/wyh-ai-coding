import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserInfo, logout as logoutApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const fetchUserInfo = async () => {
    const res = await getUserInfo()
    if (res.code === 200) {
      setUserInfo(res.data)
    }
    return res
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (e) {
      console.error(e)
    }
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    fetchUserInfo,
    logout
  }
})