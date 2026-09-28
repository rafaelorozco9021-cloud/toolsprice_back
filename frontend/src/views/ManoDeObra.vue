<template>
  <main class="bg-gray-50 min-h-screen p-3 md:p-6">
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6 md:mb-8">
      <h1 class="text-xl md:text-2xl font-bold text-gray-800">ToolsPrice <span class="text-xs md:text-sm font-normal text-gray-500">· Mano de Obra</span></h1>
      <div class="flex flex-wrap items-center gap-2 md:gap-3">
        <button @click="$router.push('/dashboard')" class="flex-1 md:flex-none px-3 md:px-4 py-2 bg-white border rounded-lg text-xs md:text-sm font-semibold hover:bg-gray-50">🏗 Materiales</button>
        <button @click="$router.push('/presupuesto')" class="flex-1 md:flex-none px-3 md:px-4 py-2 bg-purple-600 text-white rounded-lg text-xs md:text-sm font-bold hover:bg-purple-700 flex items-center justify-center gap-1">
          🛒 Presupuesto <span v-if="budgetStore.itemsCount" class="bg-white text-purple-700 text-xs px-2 py-0.5 rounded-full">{{ budgetStore.itemsCount }}</span>
        </button>
        <button @click="$router.push('/mis-facturas')" class="px-3 md:px-4 py-2 bg-white border-2 border-purple-200 text-purple-700 rounded-lg text-xs md:text-sm font-bold hover:bg-purple-50">📄 Mis Facturas</button>
        <button @click="logout" class="w-full md:w-auto text-center text-xs md:text-sm text-gray-500 hover:text-red-600 border md:border-0 border-gray-200 rounded-lg py-2 md:py-0">Cerrar sesión</button>
      </div>
    </header>

    <div v-if="budgetStore.itemsCount > 0" class="max-w-7xl mx-auto mb-4 md:mb-6">
      <div class="bg-purple-600 text-white rounded-lg px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow">
        <p class="text-sm font-semibold">🛒 Llevas <span class="font-extrabold">{{ budgetStore.itemsCount }} productos</span> ({{ budgetStore.count }} unidades) en tu presupuesto</p>
        <button @click="$router.push('/presupuesto')" class="bg-white text-purple-700 px-5 py-2 rounded-lg font-bold text-sm hover:bg-gray-100 shrink-0">Ver presupuesto →</button>
      </div>
    </div>

    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
      <!-- Buscador tabulador -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white p-4 md:p-6 rounded-lg shadow">
          <h3 class="font-bold text-gray-800 mb-2">Tabulador Mano de Obra — precios por m² / punto</h3>
          <p class="text-xs text-gray-500 mb-3">Solo mano de obra (no incluye material). Fuente: promedios Construdata/Camacol 2026.</p>
          <div class="flex gap-2 mb-3">
            <input v-model="query" @keyup.enter="search" @input="onInput" placeholder="Buscar: friso, piso ceramica, pintura, plomeria, soldadura..." class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm" />
            <button @click="clearSearch" v-if="query" class="px-3 text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div class="flex flex-wrap gap-2 mb-3">
            <button v-for="cat in categorias" :key="cat" @click="categoria=cat; search()" :class="['px-3 py-1.5 rounded-full text-xs font-semibold border', categoria===cat ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 hover:bg-gray-50']">{{ cat }}</button>
            <button @click="categoria='todas'; search()" :class="['px-3 py-1.5 rounded-full text-xs font-bold', categoria==='todas' ? 'bg-orange-500 text-white' : 'bg-gray-100 text-gray-600']">Todas</button>
          </div>
          <div class="flex gap-4">
            <button @click="search" :disabled="loading" class="flex-1 bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-60 flex items-center justify-center gap-2 text-sm min-h-[48px]">
              <svg v-if="loading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              {{ loading ? 'Buscando...' : 'Buscar en tabulador' }}
            </button>
          </div>
          <p class="text-xs text-gray-400 mt-2">Ej: <span @click="query='friso'; search()" class="underline cursor-pointer">friso</span> · <span @click="query='piso ceramica'; search()" class="underline cursor-pointer">piso cerámica</span> · <span @click="query='pintura'; search()" class="underline cursor-pointer">pintura</span></p>
        </div>

        <div v-if="loading" class="flex flex-col items-center py-12 gap-3">
          <svg class="animate-spin h-10 w-10 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          <p class="text-gray-600 font-semibold animate-pulse">Consultando tabulador...</p>
        </div>

        <div v-else-if="tasks.length>0" class="space-y-3">
          <div v-for="cat in groupedKeys" :key="cat" class="bg-white rounded-lg shadow overflow-hidden">
            <h3 class="text-sm font-bold text-white bg-gradient-to-r from-orange-500 to-purple-600 px-4 py-2 flex items-center gap-2">{{ cat }} <span class="ml-auto bg-white text-orange-600 text-xs px-2 py-1 rounded font-bold">{{ grouped[cat].length }}</span></h3>
            <div class="divide-y">
              <div v-for="t in grouped[cat]" :key="t.id" class="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-gray-800 text-sm">{{ t.nombre }}</p>
                  <p class="text-xs text-gray-500">{{ t.descripcion }} · {{ t.rendimiento }}</p>
                  <p class="text-xs text-orange-600 mt-1">{{ t.categoria }} · {{ t.incluye_material ? 'Incluye material' : 'Solo mano de obra' }}</p>
                </div>
                <div class="text-right shrink-0">
                  <p class="text-xl font-bold text-purple-600">${{ Number(t.precio_unitario).toLocaleString('es-CO') }} <span class="text-xs font-normal text-gray-500">/ {{ t.unidad }}</span></p>
                </div>
                <button @click="openQty(t)" class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-bold hover:bg-green-600 shrink-0 min-h-[40px]">Agregar</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!loading && hasSearched && tasks.length===0" class="text-center py-8 text-gray-500 text-sm">
          No se encontró "{{ lastQuery }}" en el tabulador. Prueba con friso, piso, pintura, plomería o soldadura.
        </div>
        <div v-if="!hasSearched && !loading" class="text-center py-8 text-gray-500 text-sm">
          Busca en el tabulador para comenzar — ej. "friso" o "piso ceramica"
        </div>
      </div>

      <!-- Resumen lateral ahora es solo informativo, carrito real está en /presupuesto -->
      <div class="bg-white p-4 md:p-6 rounded-lg shadow h-fit lg:sticky lg:top-6">
        <h3 class="text-lg font-bold text-gray-800 mb-1">Presupuesto</h3>
        <p class="text-xs text-gray-500 mb-4">{{ budgetStore.itemsCount }} ítems · {{ budgetStore.count }} unidades en carrito</p>
        <div v-if="budgetStore.items.length===0" class="text-gray-400 text-center py-6 border-2 border-dashed rounded-lg text-sm">Tu carrito está vacío<br/>Agrega materiales o mano de obra</div>
        <ul v-else class="space-y-2 mb-4 max-h-[30vh] overflow-auto">
          <li v-for="(it, idx) in budgetStore.items.slice(0,3)" :key="idx" class="text-xs border-b pb-2">
            <p class="font-semibold truncate">{{ it.nombre }}</p>
            <p class="text-gray-500">{{ it.quantity }} × ${{ Number(it.precio).toLocaleString('es-CO') }} = ${{ Number(it.precio*it.quantity).toLocaleString('es-CO') }}</p>
          </li>
          <li v-if="budgetStore.items.length>3" class="text-xs text-center text-gray-400">+ {{ budgetStore.items.length-3 }} más...</li>
        </ul>
        <div class="border-t pt-3 space-y-1 text-sm">
          <p>Subtotal: ${{ budgetStore.subtotal.toLocaleString('es-CO') }}</p>
          <p>IVA (16%): ${{ budgetStore.tax.toLocaleString('es-CO') }}</p>
          <p class="text-lg font-bold text-purple-600">Total: ${{ budgetStore.total.toLocaleString('es-CO') }} COP</p>
        </div>
        <button @click="$router.push('/presupuesto')" class="w-full mt-4 bg-purple-600 text-white px-4 py-3 rounded-lg font-bold hover:bg-purple-700 min-h-[48px]">Ver presupuesto →</button>
        <button @click="$router.push('/dashboard')" class="w-full mt-2 bg-white border px-4 py-2.5 rounded-lg text-sm font-semibold hover:bg-gray-50">← Seguir buscando productos</button>
        <p class="text-xs text-gray-400 mt-2 text-center">El presupuesto se guarda en "Mis Facturas" al generar PDF</p>
      </div>
    </div>

    <!-- Modal cantidad -->
    <div v-if="showQty" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="font-bold text-gray-800 mb-2">{{ qtyTask?.nombre }}</h3>
        <p class="text-xs text-gray-500 mb-3">{{ qtyTask?.categoria }} · ${{ Number(qtyTask?.precio_unitario).toLocaleString('es-CO') }} / {{ qtyTask?.unidad }}</p>
        <label class="block text-sm font-semibold mb-1">Cantidad ({{ qtyTask?.unidad }})</label>
        <div class="flex items-center gap-3 mb-4">
          <button @click="qtyVal=Math.max(1, qtyVal-1)" class="w-10 h-10 border-2 rounded-lg font-bold">−</button>
          <input v-model.number="qtyVal" type="number" min="1" class="flex-1 px-4 py-3 border-2 rounded-lg text-center font-bold text-lg" />
          <button @click="qtyVal++" class="w-10 h-10 border-2 rounded-lg font-bold">+</button>
        </div>
        <p class="text-sm mb-4">Subtotal: <b class="text-purple-600">${{ Number((qtyTask?.precio_unitario||0)*qtyVal).toLocaleString('es-CO') }}</b></p>
        <div class="flex gap-3">
          <button @click="showQty=false" class="flex-1 bg-gray-200 py-3 rounded-lg font-bold">Cancelar</button>
          <button @click="confirmQty" class="flex-1 bg-green-500 text-white py-3 rounded-lg font-bold">Agregar — {{ qtyVal }} {{ qtyTask?.unidad }}</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '../stores/budget.store.js'
const router = useRouter()
const budgetStore = useBudgetStore()
const query = ref('')
const categoria = ref('todas')
const categorias = ref(['Friso','Piso cerámica','Enchape','Mampostería','Pintura','Pisos base','Plomería','Eléctrico','Cubierta','Soldadura'])
const tasks = ref([])
const loading = ref(false)
const hasSearched = ref(false)
const lastQuery = ref('')
const showQty = ref(false)
const qtyTask = ref(null)
const qtyVal = ref(1)

const grouped = computed(() => {
  const g={}
  for(const t of tasks.value){ const c=t.categoria||'Otros'; if(!g[c]) g[c]=[]; g[c].push(t) }
  return g
})
const groupedKeys = computed(()=> Object.keys(grouped.value))

const onInput = () => { if(!query.value.trim()){ tasks.value=[]; hasSearched.value=false } }
const clearSearch = () => { query.value=''; tasks.value=[]; hasSearched.value=false }

const search = async () => {
  loading.value=true; hasSearched.value=true; lastQuery.value=query.value
  try{
    const params=new URLSearchParams({ query: query.value.trim(), limit: '50' })
    if (categoria.value && categoria.value!=='todas') params.append('categoria', categoria.value)
    const r=await fetch(`/api/labor/search?${params}`)
    const d=await r.json()
    tasks.value=d.tasks||[]
  }catch(e){ console.error(e); tasks.value=[] } finally{ loading.value=false }
}

const openQty = (t) => { qtyTask.value=t; qtyVal.value=1; showQty.value=true }
const confirmQty = () => {
  const q=Math.max(1, parseInt(qtyVal.value)||1)
  // Convertir tarea de mano de obra a formato compatible con budgetStore (precio -> precio)
  const productLike = {
    nombre: `${qtyTask.value.nombre} (${qtyTask.value.categoria} - ${qtyTask.value.unidad})`,
    categoria: qtyTask.value.categoria,
    marca: 'Mano de Obra',
    precio: qtyTask.value.precio_unitario,
    moneda: 'COP',
    unidad_medida: qtyTask.value.unidad,
    imagen_url: 'https://via.placeholder.com/300x200?text=Mano+de+Obra',
    url_producto: `mano-obra-${qtyTask.value.id}`,
    disponibilidad: true,
  }
  budgetStore.addItem(productLike, q)
  showQty.value=false
}

const logout=()=>{ localStorage.clear(); budgetStore.clear(); router.push('/') }

onMounted(async()=>{
  try{
    const r=await fetch('/api/labor/categorias')
    const d=await r.json()
    if(d.categorias) categorias.value=d.categorias
  }catch{}
  await search()
})
</script>
