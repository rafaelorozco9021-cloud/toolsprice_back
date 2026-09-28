<template>
  <main class="bg-gray-50 min-h-screen p-3 md:p-6">
    <header class="max-w-5xl mx-auto flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6 md:mb-8">
      <h1 class="text-xl md:text-2xl font-bold text-gray-800 flex items-center gap-2">ToolsPrice <span class="text-xs md:text-sm font-normal text-gray-500">· Presupuesto</span></h1>
      <div class="flex flex-wrap items-center gap-2 md:gap-3">
        <button @click="$router.push('/dashboard')" class="flex-1 md:flex-none px-4 py-2 bg-white border rounded-lg text-xs md:text-sm font-semibold hover:bg-gray-50 flex items-center justify-center gap-2">← Seguir buscando</button>
        <button @click="$router.push('/mis-facturas')" class="px-3 py-2 bg-white border-2 border-purple-200 text-purple-700 rounded-lg text-xs font-bold hover:bg-purple-50">📄 Mis Facturas</button>
        <button @click="logout" class="text-xs md:text-sm text-gray-500 hover:text-red-600">Cerrar</button>
      </div>
    </header>

    <div class="max-w-5xl mx-auto">
      <div class="bg-white rounded-lg shadow p-4 md:p-6 mb-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 class="text-xl md:text-2xl font-bold text-gray-800">Carrito de Presupuesto</h2>
            <p class="text-sm text-gray-500">{{ budgetStore.itemsCount }} productos · {{ budgetStore.count }} unidades · Homecenter</p>
          </div>
          <button v-if="budgetStore.items.length" @click="budgetStore.clear()" class="text-sm text-red-600 hover:text-red-700 border border-red-200 px-4 py-2 rounded-lg hover:bg-red-50">Vaciar carrito</button>
        </div>
      </div>

      <div v-if="budgetStore.items.length === 0" class="bg-white rounded-lg shadow p-8 md:p-12 text-center">
        <p class="text-5xl mb-4">🛒</p>
        <p class="text-gray-700 font-bold">Tu presupuesto está vacío</p>
        <p class="text-sm text-gray-500 mb-6">Agrega materiales desde el buscador y aparecerán aquí</p>
        <button @click="$router.push('/dashboard')" class="bg-purple-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-purple-700">Buscar productos</button>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="hidden md:grid grid-cols-12 gap-2 px-4 py-3 bg-gray-50 text-xs font-bold text-gray-500 uppercase">
              <span class="col-span-6">Producto</span><span class="col-span-2 text-center">Cant.</span><span class="col-span-2 text-right">P. Unit</span><span class="col-span-2 text-right">Subtotal</span>
            </div>
            <ul class="divide-y">
              <li v-for="(item, idx) in budgetStore.items" :key="item.url_producto" class="p-4 flex flex-col md:grid md:grid-cols-12 gap-3 items-start md:items-center">
                <div class="flex gap-3 col-span-6 w-full">
                  <img :src="item.imagen_url" class="w-16 h-16 object-contain bg-white border rounded p-1 shrink-0" @error="e=>e.target.src='https://via.placeholder.com/100'" />
                  <div class="flex-1 min-w-0">
                    <p class="font-semibold text-sm line-clamp-2">{{ item.nombre }}</p>
                    <p class="text-xs text-gray-500">{{ item.marca }} · {{ item.unidad_medida }} · {{ item.categoria }}</p>
                    <button @click="budgetStore.removeItem(idx)" class="md:hidden text-xs text-red-500 mt-1">Eliminar</button>
                  </div>
                </div>
                <div class="flex items-center gap-2 col-span-2 w-full md:w-auto md:justify-center">
                  <button @click="budgetStore.decQty(idx)" class="w-9 h-9 md:w-8 md:h-8 border rounded flex items-center justify-center hover:bg-gray-100 shrink-0">−</button>
                  <input v-model.number="item.quantity" type="number" min="1" class="w-16 text-center border rounded py-2 text-sm font-bold" />
                  <button @click="budgetStore.incQty(idx)" class="w-9 h-9 md:w-8 md:h-8 border rounded flex items-center justify-center hover:bg-gray-100 shrink-0">+</button>
                  <span class="md:hidden ml-auto text-xs text-gray-500">{{ item.unidad_medida }}</span>
                  <button @click="budgetStore.removeItem(idx)" class="hidden md:block text-xs text-red-500 hover:text-red-600 ml-2">Eliminar</button>
                </div>
                <div class="hidden md:block col-span-2 text-right text-sm">${{ Number(item.precio).toLocaleString('es-CO') }}</div>
                <div class="flex md:block col-span-2 justify-between items-center w-full md:w-auto md:text-right">
                  <span class="md:hidden text-sm text-gray-500">${{ Number(item.precio).toLocaleString('es-CO') }} × {{ item.quantity }}</span>
                  <span class="text-sm md:text-base font-bold">${{ Number(item.precio * item.quantity).toLocaleString('es-CO') }}</span>
                </div>
              </li>
            </ul>
          </div>
          <button @click="$router.push('/dashboard')" class="mt-4 text-sm text-purple-600 hover:text-purple-700 font-semibold">← Seguir buscando productos</button>
        </div>

        <div class="bg-white rounded-lg shadow p-4 md:p-6 h-fit lg:sticky lg:top-6">
          <h3 class="font-bold text-gray-800 mb-4">Resumen</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">Subtotal</span><span class="font-semibold">${{ budgetStore.subtotal.toLocaleString('es-CO') }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">IVA (16%)</span><span class="font-semibold">${{ budgetStore.tax.toLocaleString('es-CO') }}</span></div>
            <div class="flex justify-between text-lg font-bold text-purple-600 border-t pt-3"><span>Total</span><span>${{ budgetStore.total.toLocaleString('es-CO') }} COP</span></div>
            <p class="text-xs text-gray-400">{{ budgetStore.itemsCount }} ítems · {{ budgetStore.count }} unidades</p>
          </div>
          <label class="block text-xs font-semibold text-gray-600 mt-4 mb-1">Tipo de presupuesto</label>
          <select v-model="budgetStore.budgetType" class="w-full px-3 py-2.5 border-2 rounded-lg text-sm font-semibold">
            <option value="construccion">Construcción</option>
            <option value="soldadura">Soldadura</option>
            <option value="pintura">Pintura</option>
            <option value="plomeria">Plomería</option>
            <option value="herramientas">Herramientas</option>
            <option value="mano_obra">Mano de Obra</option>
          </select>
          <button @click="generatePDF" :disabled="generating" class="w-full mt-4 bg-purple-600 text-white py-3 rounded-lg font-bold hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2 min-h-[48px]">
            <svg v-if="generating" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
            {{ generating ? 'Generando...' : 'Generar PDF — ' + budgetTypeLabel }}
          </button>
          <p class="text-xs text-gray-400 mt-2 text-center">Se guarda en Mis Facturas y puedes reimprimir</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '../stores/budget.store.js'

const router = useRouter()
const budgetStore = useBudgetStore()
const generating = ref(false)

const budgetTypeLabel = computed(() => {
  const m = { construccion: 'Construcción', soldadura: 'Soldadura', pintura: 'Pintura', plomeria: 'Plomería', herramientas: 'Herramientas', mano_obra: 'Mano de Obra' }
  return m[budgetStore.budgetType] || budgetStore.budgetType
})

const generatePDF = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) { alert('Inicia sesión'); router.push('/login'); return }
  if (!budgetStore.items.length) return
  generating.value = true
  try {
    const payload = {
      name: `Presupuesto de ${budgetTypeLabel.value} - ${new Date().toISOString().split('T')[0]}`,
      description: `Presupuesto de ${budgetTypeLabel.value.toLowerCase()}`,
      budget_type: budgetStore.budgetType,
      tax_rate: 0.16,
      items: budgetStore.items.map(i => ({
        product_name: i.nombre,
        quantity: parseInt(i.quantity),
        unit_price: parseFloat(i.precio),
        total_price: parseFloat(i.precio) * parseInt(i.quantity)
      }))
    }
    const r = await fetch('/api/budgets/', { method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body: JSON.stringify(payload)})
    const data = await r.json()
    if (!r.ok) {
      if (r.status===401) { alert('Sesión expirada'); localStorage.clear(); router.push('/login'); return }
      throw new Error(data.detail || 'Error al guardar')
    }
    const pdf = await fetch(`/api/budgets/${data.id}/export/pdf`, { method:'POST', headers:{ Authorization:`Bearer ${token}` }})
    if (!pdf.ok) throw new Error(await pdf.text())
    const blob = await pdf.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href=url; a.download=`presupuesto_${data.id.slice(0,8)}.pdf`; a.click(); URL.revokeObjectURL(url)
    budgetStore.clear()
    router.push('/mis-facturas')
  } catch (e) {
    alert(e.message)
  } finally { generating.value=false }
}

const logout = () => { localStorage.clear(); router.push('/') }
</script>
