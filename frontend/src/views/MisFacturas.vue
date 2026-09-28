<template>
  <main class="bg-gray-50 min-h-screen p-3 md:p-6">
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6 md:mb-8">
      <div class="flex items-center gap-3 md:gap-4">
        <h1 class="text-xl md:text-2xl font-bold text-gray-800">ToolsPrice</h1>
        <span class="text-sm text-gray-400 hidden sm:inline">·</span>
        <button @click="$router.push('/dashboard')" class="text-xs md:text-sm text-purple-600 hover:text-purple-700 font-semibold">← Dashboard</button>
      </div>
      <div class="flex flex-wrap items-center gap-2 md:gap-3">
        <button @click="$router.push('/mano-de-obra')" class="flex-1 md:flex-none px-3 py-1.5 bg-orange-500 text-white rounded-full text-xs font-bold hover:bg-orange-600">👷 Mano de Obra</button>
        <span class="text-xs md:text-sm text-gray-600 hidden md:inline truncate max-w-[150px]">{{ userEmail }}</span>
        <button @click="logout" class="w-full md:w-auto text-center text-xs md:text-sm text-gray-500 hover:text-red-600 border md:border-0 border-gray-200 rounded-lg py-2 md:py-0">Cerrar sesión</button>
      </div>
    </header>

    <div class="max-w-7xl mx-auto">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <h2 class="text-xl md:text-2xl font-bold text-gray-800">Mis Facturas</h2>
        <div class="flex items-center gap-2">
          <span class="text-xs md:text-sm text-gray-500">{{ budgets.length }} presupuestos</span>
          <button @click="fetchBudgets" class="px-3 md:px-4 py-2 bg-white border rounded-lg text-xs md:text-sm hover:bg-gray-50">↻ Actualizar</button>
        </div>
      </div>

      <div v-if="loading" class="flex flex-col items-center py-16 gap-4">
        <svg class="animate-spin h-10 w-10 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <p class="text-gray-600">Cargando facturas...</p>
      </div>

      <div v-else-if="budgets.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <p class="text-4xl mb-3">📄</p>
        <p class="text-gray-700 font-semibold">No tienes facturas guardadas</p>
        <p class="text-sm text-gray-500 mb-4">Crea tu primer presupuesto en el Dashboard y aparecerá aquí</p>
        <button @click="$router.push('/dashboard')" class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700">Ir al Dashboard</button>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div v-for="b in budgets" :key="b.id" class="bg-white rounded-lg shadow hover:shadow-md transition p-5 flex flex-col">
          <div class="flex justify-between items-start gap-2 mb-3">
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-gray-800 truncate">{{ b.name }}</h3>
              <p class="text-xs text-gray-500">{{ formatDate(b.created_at) }} · <span class="capitalize">{{ labelTipo(b.budget_type || b.description) }}</span></p>
            </div>
            <span class="text-xs px-2 py-1 rounded font-bold shrink-0" :class="badgeClass(b.budget_type)">{{ labelTipo(b.budget_type) }}</span>
          </div>
          <div class="flex items-baseline gap-2 mb-3">
            <span class="text-2xl font-bold text-purple-600">${{ Number(b.total).toLocaleString('es-CO') }}</span>
            <span class="text-xs text-gray-500">COP · {{ b.status }}</span>
          </div>
          <p class="text-xs text-gray-500 mb-4">Subtotal ${{ Number(b.subtotal).toLocaleString('es-CO') }} + IVA ${{ Number(b.tax_amount).toLocaleString('es-CO') }}</p>
          <div class="mt-auto grid grid-cols-3 gap-2">
            <button @click="viewBudget(b)" class="px-3 py-2 bg-gray-100 rounded-lg text-sm font-semibold hover:bg-gray-200">👁 Ver</button>
            <button @click="editBudget(b)" class="px-3 py-2 bg-orange-100 text-orange-700 rounded-lg text-sm font-semibold hover:bg-orange-200">✎ Editar</button>
            <button @click="printBudget(b)" class="px-3 py-2 bg-purple-600 text-white rounded-lg text-sm font-semibold hover:bg-purple-700">🖨 Imprimir</button>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-2">
            <button @click="duplicateBudget(b)" class="px-3 py-2 border rounded-lg text-sm hover:bg-gray-50">⧉ Duplicar</button>
            <button @click="deleteBudget(b)" class="px-3 py-2 border border-red-200 text-red-600 rounded-lg text-sm hover:bg-red-50">🗑 Eliminar</button>
          </div>
        </div>
      </div>
    </div>

     <!-- Modal Ver -->
    <div v-if="showView" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto p-4 md:p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-bold text-gray-800">{{ viewData?.name }}</h3>
            <p class="text-sm text-gray-500">{{ viewData?.budget_type ? labelTipo(viewData.budget_type) : '' }} · {{ formatDate(viewData?.created_at) }} · #{{ viewData?.id?.slice(0,8).toUpperCase() }}</p>
          </div>
          <button @click="showView=false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
        </div>
        <div v-if="viewData?.items" class="border rounded-lg overflow-hidden mb-4 overflow-x-auto">
          <table class="w-full text-sm min-w-[480px]">
            <thead class="bg-purple-600 text-white">
              <tr><th class="px-3 py-2 text-left">Producto</th><th class="px-3 py-2 text-center">Cant.</th><th class="px-3 py-2 text-right">P.Unit</th><th class="px-3 py-2 text-right">Subtotal</th></tr>
            </thead>
            <tbody>
              <tr v-for="(it, idx) in viewData.items" :key="idx" class="border-b" :class="idx%2===0?'bg-white':'bg-gray-50'">
                <td class="px-3 py-2">{{ it.product_name }}</td>
                <td class="px-3 py-2 text-center">{{ it.quantity }}</td>
                <td class="px-3 py-2 text-right">${{ Number(it.unit_price).toLocaleString('es-CO') }}</td>
                <td class="px-3 py-2 text-right font-semibold">${{ Number(it.total_price).toLocaleString('es-CO') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="viewData" class="text-right space-y-1 text-sm mb-4">
          <p>Subtotal: ${{ Number(viewData.subtotal).toLocaleString('es-CO') }}</p>
          <p>IVA (16%): ${{ Number(viewData.tax_amount).toLocaleString('es-CO') }}</p>
          <p class="text-lg font-bold text-purple-600">Total: ${{ Number(viewData.total).toLocaleString('es-CO') }} COP</p>
        </div>
        <div class="flex gap-2">
          <button @click="showView=false" class="flex-1 bg-gray-200 py-2 rounded-lg font-semibold hover:bg-gray-300">Cerrar</button>
          <button @click="printBudget(viewData); showView=false" class="flex-1 bg-purple-600 text-white py-2 rounded-lg font-semibold hover:bg-purple-700">Reimprimir PDF</button>
        </div>
      </div>
    </div>

    <!-- Modal Editar -->
    <div v-if="showEdit" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-1">Modificar factura</h3>
        <p class="text-sm text-gray-500 mb-4">{{ editData?.name }} · {{ labelTipo(editData?.budget_type) }}</p>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Nombre</label>
        <input v-model="editData.name" class="w-full px-3 py-2 border rounded-lg mb-3" />
        <label class="block text-xs font-semibold text-gray-600 mb-1">Tipo</label>
        <select v-model="editData.budget_type" class="w-full px-3 py-2 border rounded-lg mb-4">
          <option value="construccion">Construcción</option>
          <option value="soldadura">Soldadura</option>
          <option value="pintura">Pintura</option>
          <option value="plomeria">Plomería</option>
          <option value="herramientas">Herramientas</option>
          <option value="mano_obra">Mano de Obra</option>
        </select>
        <div class="border rounded-lg overflow-hidden mb-4 overflow-x-auto">
          <table class="w-full text-sm min-w-[460px]">
            <thead class="bg-gray-100"><tr><th class="px-3 py-2 text-left text-xs">Producto</th><th class="px-3 py-2 text-center text-xs">Cant.</th><th class="px-3 py-2 text-right text-xs">Acción</th></tr></thead>
            <tbody>
              <tr v-for="(it, idx) in editData.items" :key="idx" class="border-b">
                <td class="px-3 py-2">
                  <p class="font-semibold text-sm">{{ it.product_name }}</p>
                  <p class="text-xs text-gray-500">${{ Number(it.unit_price).toLocaleString('es-CO') }} c/u</p>
                </td>
                <td class="px-3 py-2 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <button @click="it.quantity = Math.max(1, it.quantity-1)" class="w-7 h-7 border rounded hover:bg-gray-100">−</button>
                    <input v-model.number="it.quantity" type="number" min="1" class="w-14 text-center border rounded py-1" />
                    <button @click="it.quantity++" class="w-7 h-7 border rounded hover:bg-gray-100">+</button>
                  </div>
                </td>
                <td class="px-3 py-2 text-right"><button @click="editData.items.splice(idx,1)" class="text-red-500 text-xs hover:underline">Eliminar</button></td>
              </tr>
              <tr v-if="editData.items.length===0"><td colspan="3" class="px-3 py-4 text-center text-gray-400">Sin productos — elimina la factura si no necesitas</td></tr>
            </tbody>
          </table>
        </div>
        <div class="flex gap-2">
          <button @click="showEdit=false" class="flex-1 bg-gray-200 py-2 rounded-lg font-semibold hover:bg-gray-300">Cancelar</button>
          <button @click="saveEdit" class="flex-1 bg-orange-500 text-white py-2 rounded-lg font-semibold hover:bg-orange-600">Guardar cambios</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const budgets = ref([])
const loading = ref(false)
const showView = ref(false)
const viewData = ref(null)
const showEdit = ref(false)
const editData = ref(null)
const userEmail = ref(localStorage.getItem('user_email') || '')

const labelTipo = (t) => {
  const m = { construccion: 'Construcción', soldadura: 'Soldadura', pintura: 'Pintura', plomeria: 'Plomería', herramientas: 'Herramientas', mano_obra: 'Mano de Obra' }
  if (!t) return 'General'
  const low = t.toLowerCase()
  const key = low.includes('mano') ? 'mano_obra' : low.includes('soldadura') ? 'soldadura' : low.includes('pintura') ? 'pintura' : low.includes('plomeria') ? 'plomeria' : low.includes('herramienta') ? 'herramientas' : low.trim()
  return m[key] || t
}
const badgeClass = (t) => {
  const c = { construccion: 'bg-orange-100 text-orange-700', soldadura: 'bg-gray-800 text-white', pintura: 'bg-blue-100 text-blue-700', plomeria: 'bg-cyan-100 text-cyan-700', herramientas: 'bg-green-100 text-green-700', mano_obra: 'bg-purple-100 text-purple-700' }
  return c[(t||'construccion').toLowerCase()] || 'bg-gray-100 text-gray-700'
}
const formatDate = (d) => {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' }) } catch { return d.slice(0,10) }
}

const authHeaders = () => {
  const token = localStorage.getItem('access_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const fetchBudgets = async () => {
  loading.value = true
  try {
    const r = await fetch('/api/budgets/', { headers: { ...authHeaders() } })
    if (r.status === 401) { alert('Sesión expirada, inicia sesión'); localStorage.removeItem('access_token'); router.push('/login'); return }
    const data = await r.json()
    budgets.value = Array.isArray(data) ? data : []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const viewBudget = async (b) => {
  try {
    const r = await fetch(`/api/budgets/${b.id}`, { headers: authHeaders() })
    viewData.value = await r.json()
    showView.value = true
  } catch (e) { alert('Error al consultar factura') }
}

const editBudget = async (b) => {
  try {
    const r = await fetch(`/api/budgets/${b.id}`, { headers: authHeaders() })
    const data = await r.json()
    // clonar para edición
    editData.value = JSON.parse(JSON.stringify(data))
    if (!editData.value.budget_type) editData.value.budget_type = 'construccion'
    showEdit.value = true
  } catch (e) { alert('Error al cargar para editar') }
}

const saveEdit = async () => {
  if (!editData.value || editData.value.items.length === 0) { alert('Debe tener al menos 1 producto'); return }
  // recalcular total local no necesario, backend lo hace
  const payload = {
    name: editData.value.name,
    description: editData.value.description || `Presupuesto de ${editData.value.budget_type}`,
    budget_type: editData.value.budget_type,
    tax_rate: 0.16,
    items: editData.value.items.map(it => ({
      product_name: it.product_name,
      quantity: parseInt(it.quantity),
      unit_price: parseFloat(it.unit_price),
      total_price: parseFloat(it.unit_price) * parseInt(it.quantity)
    }))
  }
  try {
    const r = await fetch(`/api/budgets/${editData.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload)
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Error al guardar')
    showEdit.value = false
    await fetchBudgets()
    alert('Factura actualizada correctamente')
  } catch (e) { alert(e.message) }
}

const deleteBudget = async (b) => {
  if (!confirm(`¿Eliminar factura "${b.name}"?`)) return
  try {
    const r = await fetch(`/api/budgets/${b.id}`, { method: 'DELETE', headers: authHeaders() })
    if (!r.ok) throw new Error('No se pudo eliminar')
    await fetchBudgets()
  } catch (e) { alert(e.message) }
}

const duplicateBudget = async (b) => {
  try {
    const r = await fetch(`/api/budgets/${b.id}/duplicate`, { method: 'POST', headers: authHeaders() })
    if (!r.ok) throw new Error('No se pudo duplicar')
    await fetchBudgets()
    alert('Factura duplicada')
  } catch (e) { alert(e.message) }
}

const printBudget = async (b) => {
  try {
    const r = await fetch(`/api/budgets/${b.id}/export/pdf`, { method: 'POST', headers: authHeaders() })
    if (!r.ok) { const t=await r.text(); throw new Error(t.slice(0,200)) }
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `factura_${b.id.slice(0,8)}.pdf`; a.click()
    URL.revokeObjectURL(url)
  } catch (e) { alert('Error al imprimir: ' + e.message) }
}

const logout = () => { localStorage.removeItem('access_token'); router.push('/') }

onMounted(fetchBudgets)
</script>
