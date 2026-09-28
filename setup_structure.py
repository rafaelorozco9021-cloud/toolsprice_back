import os
import shutil

# Create directory structure

dirs = [
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db/models",
    "backend/app/db/migrations",
    "backend/app/scrapers",
    "backend/app/services",
    "backend/app/schemas",
    "frontend/src/assets",
    "frontend/src/components/landing",
    "frontend/src/components/app",
    "frontend/src/views",
    "frontend/src/stores",
    "frontend/src/services",
    "frontend/src/router",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

print("Structure created successfully")

```