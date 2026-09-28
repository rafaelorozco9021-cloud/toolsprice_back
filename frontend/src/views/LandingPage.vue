<template>
  <main class="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 min-h-screen">
    <header class="p-4 md:p-6">
      <nav class="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-white">
        <h1 class="text-xl md:text-2xl font-bold">ToolsPrice</h1>
        <div class="flex flex-wrap items-center gap-3 text-sm">
          <button @click="$router.push('/dashboard')" class="px-4 py-2 bg-white/20 rounded-full hover:bg-white/30">App</button>
          <button @click="$router.push('/login')" class="px-4 py-2 bg-white text-purple-600 rounded-full font-bold hover:bg-gray-100">Iniciar sesión</button>
        </div>
      </nav>
    </header>

    <section class="hero text-center text-white py-12 md:py-20 px-4">
      <h2 class="text-3xl md:text-5xl font-bold mb-4 md:mb-6 leading-tight">Arma el presupuesto de tu obra en minutos</h2>
      <p class="text-base md:text-xl mb-6 md:mb-8 max-w-2xl mx-auto">Precios reales de Homecenter, comparación automática y presupuestos exportables en PDF.</p>
      <button @click="goToRegister" class="w-full sm:w-auto bg-white text-purple-600 px-8 py-3 rounded-full font-semibold text-base md:text-lg hover:bg-gray-100 min-h-[48px]">Crear cuenta gratis</button>
    </section>

    <section class="how-it-works bg-white py-12 md:py-16 px-4">
      <h2 class="text-2xl md:text-3xl font-bold text-center text-gray-800 mb-8 md:mb-12">Cómo funciona</h2>
      <div class="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4"><span class="text-2xl font-bold text-purple-600">1</span></div>
          <h3 class="font-semibold text-lg mb-2">Regístrate</h3>
          <p class="text-gray-600">Crea tu cuenta en segundos</p>
        </div>
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4"><span class="text-2xl font-bold text-purple-600">2</span></div>
          <h3 class="font-semibold text-lg mb-2">Busca materiales</h3>
          <p class="text-gray-600">Encuentra lo que necesitas</p>
        </div>
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4"><span class="text-2xl font-bold text-purple-600">3</span></div>
          <h3 class="font-semibold text-lg mb-2">Compara precios</h3>
          <p class="text-gray-600">Ver precios de varias tiendas</p>
        </div>
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4"><span class="text-2xl font-bold text-purple-600">4</span></div>
          <h3 class="font-semibold text-lg mb-2">Exporta PDF</h3>
          <p class="text-gray-600">Descarga tu presupuesto</p>
        </div>
      </div>
    </section>

    <section class="benefits bg-gray-50 py-12 md:py-16 px-4">
      <h2 class="text-2xl md:text-3xl font-bold text-center text-gray-800 mb-8 md:mb-12">Beneficios</h2>
      <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="font-semibold text-lg mb-2">Ahorro de tiempo</h3>
          <p class="text-gray-600">No más visitas a tiendas, compara todo desde casa</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="font-semibold text-lg mb-2">Precios actualizados</h3>
          <p class="text-gray-600">Datos en tiempo real de las tiendas</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="font-semibold text-lg mb-2">Presupuestos guardables</h3>
          <p class="text-gray-600">Accede a tu historial cuando lo necesites</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="font-semibold text-lg mb-2">Exportación PDF</h3>
          <p class="text-gray-600">Documentos profesionales listos para compartir</p>
        </div>
      </div>
    </section>

    <section class="stores bg-white py-12 md:py-16 px-4">
      <h2 class="text-2xl md:text-3xl font-bold text-center text-gray-800 mb-8 md:mb-12">Tienda oficial</h2>
      <div class="flex flex-col sm:flex-row justify-center gap-4 md:gap-8 items-center flex-wrap">
        <div class="text-2xl md:text-3xl font-extrabold text-orange-600">Homecenter</div>
        <span class="text-gray-400 hidden sm:inline">·</span>
        <div class="text-base md:text-lg text-gray-600">homecenter.com.co</div>
      </div>
      <p class="text-center text-xs md:text-sm text-gray-500 mt-4 px-4">Scraping exclusivo de Homecenter — Todas las categorías • Precios y características en tiempo real</p>
    </section>

    <footer class="bg-gray-800 text-white py-8 px-4">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center">
        <p>© 2026 ToolsPrice. Todos los derechos reservados.</p>
        <div class="space-x-4 mt-4 md:mt-0">
          <a href="#" class="hover:text-purple-300">Términos</a>
          <a href="#" class="hover:text-purple-300">Privacidad</a>
          <a href="#" class="hover:text-purple-300">Contacto</a>
        </div>
      </div>
    </footer>
  </main>
</template>

<script setup>
const goToRegister = () => {
  window.location.href = '/register'
}
</script>
