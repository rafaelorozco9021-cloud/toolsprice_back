# ToolsPrice

Sistema web para generar presupuestos de obras con precios en tiempo real de Homecenter (homecenter.com.co) — categoría Materiales de Construcción.

## Setup rápido

```bash
docker-compose up --build
```

## Variables de entorno
```env
DATABASE_URL=postgresql://user:pass@localhost/toolsprece
REDIS_URL=redis://localhost
SECRET_KEY=change_me
JWT_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASS=pass
```

## Tienda oficial
- **Homecenter** (homecenter.com.co) — Scraping exclusivo categoría Materiales de Construcción con HTTPX + BeautifulSoup + ld+json

## Documentación API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura del proyecto

```
toolsprice/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # Rutas FastAPI
│   │   ├── core/            # Config, seguridad, celery
│   │   ├── db/              # Modelos SQLAlchemy
│   │   ├── scrapers/        # Scrapers por tienda
│   │   ├── services/        # Lógica de negocio
│   │   └── schemas/         # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # Páginas (Landing, Dashboard, Login, Register)
│   │   ├── components/      # Componentes reutilizables
│   │   ├── router/          # Configuración de Vue Router
│   │   └── main.js
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Funcionalidades principales

### Backend
- ✅ Autenticación JWT (registro, login, verificación de email)
- ✅ Scraping modular Homecenter (httpx + ld+json + __NEXT_DATA__)
- ✅ Búsqueda de productos con filtros
- ✅ Gestión de presupuestos (construcción/soldadura/pintura/plomería) + 4 tipos
- ✅ Exportación a PDF con firma digital ToolsPrice

### Frontend
- ✅ Landing page moderna y responsive
- ✅ Dashboard con búsqueda y panel de presupuesto
- ✅ Login y Registro con validación
- ✅ Generación y descarga de PDF

## Próximos pasos
1. Integrar Celery para scraping programado
2. Añadir validación de email real (SMTP)
3. Mejorar matching de productos entre tiendas
4. Añadir autenticación con OAuth (Google, Microsoft)
5. Implementar sistema de planes (free/premium)
