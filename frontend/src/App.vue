<template>
  <router-view />
  <!-- Modal extender sesión (aparece 5 min antes de expirar) -->
  <div v-if="showExtend" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[100] p-4">
    <div class="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl border-2 border-purple-200">
      <div class="flex items-center gap-3 mb-3">
        <span class="w-10 h-10 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-xl">⏰</span>
        <h3 class="text-lg font-bold text-gray-800">Tu sesión está por expirar</h3>
      </div>
      <p class="text-sm text-gray-600 mb-2">Te quedan <span class="font-bold text-purple-600">{{ minutes }}:{{ seconds.padStart(2,'0') }}</span> para que expire la sesión.</p>
      <p class="text-xs text-gray-500 mb-5">¿Quieres extenderla 60 minutos más?</p>
      <div class="flex gap-3">
        <button @click="logoutExtend" class="flex-1 px-4 py-3 border rounded-lg font-semibold hover:bg-gray-100">Cerrar sesión</button>
        <button @click="extendSession" :disabled="extending" class="flex-1 bg-purple-600 text-white px-4 py-3 rounded-lg font-bold hover:bg-purple-700 disabled:opacity-60 flex items-center justify-center gap-2">
          <svg v-if="extending" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          {{ extending ? 'Extendiendo...' : 'Extender 60 min' }}
        </button>
      </div>
      <p v-if="extendError" class="text-xs text-red-500 mt-3 text-center">{{ extendError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showExtend = ref(false)
const remainingMs = ref(0)
const extending = ref(false)
const extendError = ref('')
let timer = null

const minutes = computed(() => String(Math.floor(remainingMs.value / 60000)))
const seconds = computed(() => String(Math.floor((remainingMs.value % 60000) / 1000)))

function decodeExp(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')))
    if (payload.exp) return payload.exp * 1000
  } catch {}
  return null
}

function getExp() {
  const stored = localStorage.getItem('access_token_exp')
  if (stored) return parseInt(stored)
  const token = localStorage.getItem('access_token')
  if (token) {
    const exp = decodeExp(token)
    if (exp) return exp
  }
  return null
}

function check() {
  const exp = getExp()
  const token = localStorage.getItem('access_token')
  if (!exp || !token) {
    showExtend.value = false
    return
  }
  const now = Date.now()
  const remaining = exp - now
  remainingMs.value = Math.max(0, remaining)
  // mostrar cuando queden <=5 min y aún queda tiempo
  if (remaining > 0 && remaining <= 5*60*1000) {
    showExtend.value = true
  } else if (remaining <= 0) {
    // expirado
    showExtend.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('access_token_exp')
    if (router.currentRoute.value.meta.requiresAuth) router.push('/login')
  } else {
    showExtend.value = false
  }
}

async function extendSession() {
  extending.value = true
  extendError.value = ''
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) {
    extendError.value = 'No hay refresh_token, inicia sesión nuevamente'
    extending.value = false
    return
  }
  try {
    const r = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh })
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'No se pudo extender')
    localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    // reset 60 min
    localStorage.setItem('access_token_exp', Date.now() + 60*60*1000)
    showExtend.value = false
  } catch (e) {
    extendError.value = e.message
  } finally {
    extending.value = false
  }
}

function logoutExtend() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('access_token_exp')
  localStorage.removeItem('user_email')
  showExtend.value = false
  router.push('/login')
}

onMounted(() => {
  check()
  timer = setInterval(check, 10000) // revisa cada 10s
  // escuchar cambios de token (login)
  window.addEventListener('storage', check)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('storage', check)
})
</script>
