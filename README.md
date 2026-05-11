# ProyectoFinal_TLF

Búsqueda y validación de patrones en textos y sistemas interactivos.

**Proyecto final — Teoría de Lenguajes Formales**
**Universidad del Quindío — Ingeniería de Sistemas y Computación**

---

## ⚡ Instalación rápida

Descarga el ejecutable para tu sistema operativo desde
**[GitHub Releases](https://github.com/lyc4nthrope/ProyectoFinal_TLF/releases)**:

| Sistema | Archivo |
|---------|---------|
| 🐧 Linux | `tlf-linux` |
| 🍎 macOS | `tlf-macos` |
| 🪟 Windows | `tlf-windows.exe` |

```bash
# Linux / macOS
chmod +x tlf-linux
./tlf-linux ui              # Interfaz gráfica
./tlf-linux scan "texto"    # Buscar patrones
./tlf-linux validate phone "3001234567"  # Validar un campo

# Windows (doble clic o terminal)
tlf-windows.exe ui
```

> **Nota**: Los releases incluyen 3 ejecutables, uno para cada sistema operativo.
> Se generan automáticamente al crear un tag `v*` en GitHub.

---

## 🐍 Uso desde código fuente

```bash
# 1. Clonar
git clone https://github.com/lyc4nthrope/ProyectoFinal_TLF.git
cd ProyectoFinal_TLF

# 2. Ejecutar directamente (sin instalación)
python3 -m src.main ui                               # Interfaz gráfica
python3 -m src.main scan "Llama al 3001234567"       # Buscar patrones
python3 -m src.main validate phone "3001234567"      # Validar un campo

# 3. O instalar como comando global
pip install -e .
tlf ui                                               # Mismo resultado
```

### Requisitos

- **Python 3.10 o superior**
- Sin dependencias externas (solo librería estándar)

---

## 📦 ¿Qué hace?

Aplicación en Python que detecta y valida patrones en textos mediante
**autómatas finitos deterministas (AFD)** implementados manualmente, sin usar
librerías de expresiones regulares predefinidas.

### Dos modos de uso

| Modo | Descripción |
|------|-------------|
| 🔍 **Scanner** (Parte A) | Pega un texto y encuentra todos los patrones válidos automáticamente |
| 📝 **Formularios** (Parte B) | 6 campos con validación en tiempo real, guía visual y grafo del autómata |

---

## 🧩 Patrones soportados

| Patrón | Formato | Scanner | Formulario |
|--------|---------|:-------:|:----------:|
| 📞 Teléfono | 10-13 dígitos, prefijo `+` opcional | ✅ | ✅ |
| 📧 Correo | `local@dominio.tld` | ✅ | ✅ |
| 📅 Fecha | `DD/MM/AAAA` (1900-2100) | ✅ | ✅ |
| 🚗 Placa | `LLLDDD` (carro) / `LLLDDDL` (moto) | ✅ | ✅ |
| 🌐 URL | `http(s)://dominio.tld[/ruta]` | ✅ | — |
| 📋 NIT | `NNN.NNN.NNN-D` (colombiano) | ✅ | ✅ |
| 🔒 Contraseña | 8+ chars, mayúscula, minúscula, dígito, símbolo | — | ✅ |

---

## 📁 Estructura del proyecto

```
src/
  core/          -- TraceableAutomaton, ValidationResult, symbol_classifier
  patterns/      -- 7 validadores AFD + scanner de texto libre
  ui/            -- Interfaz Tkinter (formularios con validación)
  main.py        -- CLI: scan, validate, ui
tests/           -- 115 pruebas unitarias
docs/            -- Documentación formal del proyecto
.github/
  workflows/
    test.yml     -- Tests automáticos en cada push
    release.yml  -- Build multiplataforma + GitHub Release
```

---

## 🧪 Tests

```bash
python3 -m pytest tests/ -q
# 115 passed
```

Los tests se ejecutan automáticamente en **Linux, macOS y Windows**
(con Python 3.10 a 3.13) en cada `git push` mediante GitHub Actions.

---

## 🚀 CI/CD

| Acción | Evento | Resultado |
|--------|--------|-----------|
| `git push` | Cualquier branch | ✅ Tests automáticos en 12 combinaciones OS×Python |
| `git tag v1.0.0` + `git push --tags` | Tag `v*` | 📦 Build de ejecutables + Release en GitHub |

---

## 👥 Créditos

- Cristhian Eduardo Osorio Restrepo
- Daniel Stiven Perez Cordoba

**Universidad del Quindío — Teoría de Lenguajes Formales — 2025**
