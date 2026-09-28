<template>
  <main class="bg-gray-50 min-h-screen p-3 md:p-6">
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6 md:mb-8">
      <h1 class="text-xl md:text-2xl font-bold text-gray-800 flex items-center gap-2">ToolsPrice <span class="text-xs md:text-sm font-normal text-gray-500">· Homecenter</span></h1>
      <div class="flex flex-wrap items-center gap-2 md:gap-3">
        <button @click="$router.push('/mano-de-obra')" class="flex-1 md:flex-none px-3 md:px-4 py-2 bg-orange-500 text-white rounded-lg text-xs md:text-sm font-bold hover:bg-orange-600">👷 Mano de Obra</button>
        <button @click="$router.push('/mis-facturas')" class="flex-1 md:flex-none px-3 md:px-4 py-2 bg-white border-2 border-purple-200 text-purple-700 rounded-lg text-xs md:text-sm font-bold hover:bg-purple-50">📄 Mis Facturas</button>
        <button @click="logout" class="w-full md:w-auto text-center text-purple-600 hover:text-purple-700 text-xs md:text-sm border md:border-0 border-purple-200 rounded-lg py-2 md:py-0">Cerrar sesión</button>
      </div>
    </header>

    <!-- Aviso presupuesto tipo carrito -->
    <div v-if="budgetStore.itemsCount > 0" class="max-w-7xl mx-auto mb-4 md:mb-6">
      <div class="bg-purple-600 text-white rounded-lg px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow">
        <p class="text-sm font-semibold">🛒 Llevas <span class="font-extrabold">{{ budgetStore.itemsCount }} productos</span> ({{ budgetStore.count }} unidades) en tu presupuesto</p>
        <button @click="$router.push('/presupuesto')" class="bg-white text-purple-700 px-5 py-2 rounded-lg font-bold text-sm hover:bg-gray-100 shrink-0">Ver presupuesto →</button>
      </div>
    </div>

    <div class="max-w-7xl mx-auto">
      <div class="bg-white p-4 md:p-6 rounded-lg shadow mb-6">
        <div class="relative">
          <input 
            v-model="searchQuery" 
            @keyup.enter="search"
            @input="onInput"
            placeholder="Buscar materiales (cemento, varilla, brocha, tubo pvc...)" 
            class="w-full px-4 py-3 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm md:text-base"
          />
          <button v-if="searchQuery" @click="clearSearch" class="absolute right-3 top-3 text-gray-400 hover:text-gray-600 w-8 h-8 flex items-center justify-center">✕</button>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 mt-4">
          <button @click="search" :disabled="loading" class="flex-1 bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm md:text-base min-h-[48px]">
            <svg v-if="loading" class="animate-spin h-5 w-5 text-white shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ loading ? 'Buscando...' : 'Buscar en Homecenter' }}
          </button>
          <span class="px-4 py-3 bg-orange-50 text-orange-700 border border-orange-200 rounded-lg text-xs md:text-sm flex items-center justify-center shrink-0">Todas las categorías</span>
        </div>
        <p class="text-xs text-gray-400 mt-3 text-center md:text-left">Tip: tu presupuesto se guarda y puedes verlo en <button @click="$router.push('/presupuesto')" class="underline text-purple-600">Ver presupuesto</button></p>
      </div>

      <div v-if="loading" class="flex flex-col items-center justify-center py-12 gap-4">
        <svg class="animate-spin h-10 w-10 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <p class="text-gray-600 font-semibold animate-pulse">Buscando en Homecenter (todas las categorías)...</p>
        <p class="text-sm text-gray-400">Esto puede tardar hasta 10 segundos</p>
      </div>

      <div v-else>
        <div v-for="(group, categoria) in groupedResults" :key="categoria" class="mb-6">
          <h3 class="text-sm font-bold text-white bg-gradient-to-r from-purple-600 to-orange-500 px-4 py-2 rounded-lg mb-3 flex items-center gap-2">
            <span>{{ categoria }}</span> <span class="ml-auto bg-white text-purple-700 text-xs px-2 py-1 rounded font-bold">{{ group.length }} productos</span>
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="product in group" :key="product.url_producto" class="bg-white rounded-lg shadow flex flex-col overflow-hidden hover:shadow-lg transition">
              <div class="w-full h-52 bg-white flex items-center justify-center p-4 border-b">
                <img 
                  :src="product.imagen_url || 'https://via.placeholder.com/300x200?text=Sin+imagen'" 
                  :alt="product.nombre" 
                  class="max-w-full max-h-full object-contain"
                  loading="lazy"
                  @error="e => e.target.src='https://via.placeholder.com/300x200?text=Sin+imagen'"
                />
              </div>
              <div class="p-4 flex flex-col flex-1">
                <h3 class="font-semibold text-gray-800 line-clamp-2 min-h-[3rem] text-sm">{{ product.nombre }}</h3>
                <p class="text-xs text-gray-500 mt-1">{{ product.categoria }}</p>
                <p class="text-xl font-bold text-purple-600 my-2">${{ Number(product.precio).toLocaleString('es-CO') }} <span class="text-xs font-normal text-gray-500">{{ product.moneda }}</span></p>
                <p class="text-xs text-gray-500 mb-1">Marca: {{ product.marca || '—' }} · {{ product.unidad_medida }}</p>
                <p class="text-xs text-orange-600 mb-3">Homecenter · {{ product.disponibilidad ? 'Disponible' : 'Agotado' }}</p>
                <div class="mt-auto">
                  <button @click="openQtyModal(product)" class="w-full bg-green-500 text-white px-4 py-2.5 rounded font-semibold hover:bg-green-600 min-h-[44px]">Agregar al presupuesto</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="results.length === 0 && !loading" class="text-center py-8 text-gray-500">
        <p v-if="hasSearched">No se encontraron productos para "{{ lastQuery }}" en Homecenter. Prueba con "cemento", "varilla", "arena" o "ladrillo".</p>
        <p v-else>Busca materiales para comenzar — scraping en vivo de Homecenter</p>
      </div>
    </div>

    <!-- Modal cantidad -->
    <div v-if="showQtyModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
        <h3 class="text-lg font-bold text-gray-800 mb-2">¿Cuántos necesitas?</h3>
        <div class="flex gap-3 mb-4 bg-gray-50 p-3 rounded">
          <img :src="qtyProduct?.imagen_url" class="w-20 h-20 object-contain bg-white rounded border p-1" />
          <div class="flex-1">
            <p class="font-semibold text-sm line-clamp-2">{{ qtyProduct?.nombre }}</p>
            <p class="text-xs text-gray-500">{{ qtyProduct?.marca }} · {{ qtyProduct?.unidad_medida }}</p>
            <p class="text-purple-600 font-bold">${{ Number(qtyProduct?.precio).toLocaleString('es-CO') }} {{ qtyProduct?.moneda }}</p>
          </div>
        </div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Cantidad ({{ qtyProduct?.unidad_medida }})</label>
        <div class="flex items-center gap-3 mb-6">
          <button @click="qtyValue = Math.max(1, qtyValue - 1)" class="w-10 h-10 rounded-lg border-2 font-bold hover:bg-gray-100">−</button>
          <input v-model.number="qtyValue" type="number" min="1" class="flex-1 px-4 py-3 border-2 rounded-lg text-center font-bold text-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
          <button @click="qtyValue++" class="w-10 h-10 rounded-lg border-2 font-bold hover:bg-gray-100">+</button>
        </div>
        <p class="text-sm text-gray-600 mb-4">Subtotal: <span class="font-bold text-purple-600">${{ Number((qtyProduct?.precio || 0) * qtyValue).toLocaleString('es-CO') }}</span></p>
        <div class="flex gap-3">
          <button @click="showQtyModal = false" class="flex-1 bg-gray-200 px-4 py-3 rounded-lg font-semibold hover:bg-gray-300">Cancelar</button>
          <button @click="confirmAddToBudget" class="flex-1 bg-green-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-green-600">Agregar — {{ qtyValue }} ×</button>
        </div>
        <p class="text-xs text-center text-gray-400 mt-3">Se agregará a <button @click="confirmAddToBudget(); $router.push('/presupuesto')" class="underline text-purple-600">Ver presupuesto</button></p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '../stores/budget.store.js'

const router = useRouter()
const budgetStore = useBudgetStore()

const searchQuery = ref('')
const loading = ref(false)
const results = ref([])
const hasSearched = ref(false)
const lastQuery = ref('')

const showQtyModal = ref(false)
const qtyProduct = ref(null)
const qtyValue = ref(1)

const groupedResults = computed(() => {
  const groups = {}
  for (const p of results.value) {
    const cat = p.categoria || 'Homecenter'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(p)
  }
  return groups
})

watch(searchQuery, (val) => {
  if (!val.trim()) {
    results.value = []
    hasSearched.value = false
    lastQuery.value = ''
  }
})
const onInput = () => {
  if (!searchQuery.value.trim()) {
    results.value = []
    hasSearched.value = false
  }
}
const clearSearch = () => {
  searchQuery.value = ''
  results.value = []
  hasSearched.value = false
  lastQuery.value = ''
}

const search = async () => {
  if (!searchQuery.value.trim()) return
  loading.value = true
  hasSearched.value = true
  lastQuery.value = searchQuery.value
  try {
    const params = new URLSearchParams({ query: searchQuery.value, store: 'Homecenter' })
    const response = await fetch(`/api/products/search?${params}`)
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Error en búsqueda')
    results.value = data.products || []
  } catch (error) {
    console.error('Error searching:', error)
    results.value = []
  } finally {
    loading.value = false
  }
}

const openQtyModal = (product) => {
  qtyProduct.value = product
  qtyValue.value = 1
  showQtyModal.value = true
}

const confirmAddToBudget = () => {
  const qty = Math.max(1, parseInt(qtyValue.value) || 1)
  budgetStore.addItem(qtyProduct.value, qty)
  showQtyModal.value = false
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_email')
  localStorage.removeItem('access_token_exp')
  budgetStore.clear()
  router.push('/')
}
</script>
