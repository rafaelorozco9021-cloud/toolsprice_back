<template>
  <div class="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white p-6 md:p-8 rounded-lg shadow-lg max-w-md w-full">
      <div class="text-center mb-6">
        <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-orange-500">ToolsPrice</h1>
        <p class="text-xs font-semibold tracking-widest text-gray-400 uppercase mt-1">Homecenter · Presupuestos</p>
      </div>
      <h2 class="text-2xl font-bold text-center text-gray-800 mb-1">Iniciar sesión</h2>
      <p class="text-center text-gray-500 text-sm mb-6">Bienvenido a ToolsPrice</p>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold mb-2">Email</label>
          <input v-model="form.email" type="email" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base" required />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 font-semibold mb-2">Contraseña</label>
          <input v-model="form.password" type="password" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base" required />
        </div>
        <button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 min-h-[48px]">Iniciar sesión</button>
      </form>

      <p class="text-center text-gray-600 mt-6">
        ¿No tienes cuenta? <router-link to="/register" class="text-purple-600 hover:text-purple-700 font-semibold">Regístrate</router-link>
      </p>

      <p v-if="error" class="text-red-500 text-sm text-center mt-4">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const error = ref('')

const form = ref({
  email: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''

  try {
    const params = new URLSearchParams()
    params.append('username', form.value.email)
    params.append('password', form.value.password)

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    })

    const data = await response.json()

    if (response.ok) {
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user_email', form.value.email)
      // 60 min de sesión + 5 min de aviso
      localStorage.setItem('access_token_exp', Date.now() + 60*60*1000)
      localStorage.setItem('refresh_token_exp', Date.now() + 30*24*60*60*1000)
      router.push('/dashboard')
    } else {
      error.value = data.detail || 'Error al iniciar sesión'
    }
  } catch (err) {
    error.value = 'Error de conexión'
  }
}
</script>
