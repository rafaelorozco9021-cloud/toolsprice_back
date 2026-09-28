import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))

  async function login(email, password) {
    // Llamada al backend
    token.value = 'token'
    localStorage.setItem('access_token', token.value)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  return { user, token, login, logout }
})

```