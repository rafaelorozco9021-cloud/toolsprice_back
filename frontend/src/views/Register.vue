<template>
  <div class="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white p-6 md:p-8 rounded-lg shadow-lg max-w-md w-full max-h-[90vh] overflow-auto">
      <div class="text-center mb-6">
        <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-orange-500">ToolsPrice</h1>
        <p class="text-xs font-semibold tracking-widest text-gray-400 uppercase mt-1">Homecenter · Presupuestos</p>
      </div>
      <h2 class="text-2xl font-bold text-center text-gray-800 mb-1">Crear cuenta</h2>
      <p class="text-center text-gray-500 text-sm mb-6">Únete a ToolsPrice</p>

      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold mb-2">Nombre</label>
          <input v-model="form.name" type="text" class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500" required />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold mb-2">Email</label>
          <input v-model="form.email" type="email" class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500" required />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold mb-2">Contraseña</label>
          <input v-model="form.password" type="password" class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500" required />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 font-semibold mb-2">Confirmar contraseña</label>
          <input v-model="form.password_confirm" type="password" class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500" required />
        </div>
        <button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700">Registrarse</button>
      </form>

      <p class="text-center text-gray-600 mt-6">
        ¿Ya tienes cuenta? <router-link to="/login" class="text-purple-600 hover:text-purple-700 font-semibold">Inicia sesión</router-link>
      </p>

      <p v-if="error" class="text-red-500 text-sm text-center mt-4">{{ error }}</p>
      <p v-if="success" class="text-green-500 text-sm text-center mt-4">{{ success }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const error = ref('')
const success = ref('')

const form = ref({
  name: '',
  email: '',
  password: '',
  password_confirm: ''
})

const handleRegister = async () => {
  error.value = ''
  success.value = ''

  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()

    if (response.ok) {
      success.value = '¡Registro exitoso! Inicia sesión para continuar.'
      form.value = { name: '', email: '', password: '', password_confirm: '' }
      setTimeout(() => router.push('/login'), 2000)
    } else {
      error.value = data.detail || 'Error al registrar'
    }
  } catch (err) {
    error.value = 'Error de conexión'
  }
}
</script>
