# Esencial Reembolsos MCP Server

MCP server para consultar y gestionar reembolsos de **Isapre Esencial** desde cualquier cliente MCP compatible (Claude Desktop, ChatGPT, etc.).

## Requisitos

- macOS (usa `osascript` para diálogos nativos)
- Google Chrome instalado en `/Applications/`
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Instalación

```bash
git clone <repo>
cd esencial-reembolsos-mcp
uv sync
uv run playwright install chromium
```

Agrega al `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "esencial-reembolsos": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/esencial-reembolsos-mcp", "esencial-mcp"]
    }
  }
}
```

> **Nota:** La sesión se guarda en el **Keychain de macOS**. La primera vez que se autentica, macOS puede pedir tu contraseña o Touch ID para autorizar el acceso — esto es esperado y seguro.

## Tools disponibles

| Tool | Descripción |
|---|---|
| `about` | Información del servidor |
| `auth` | Abre Chrome para hacer login en Isapre Esencial |
| `logout` | Elimina la sesión guardada del Keychain |

## Roadmap

- [x] Autenticación interactiva con Chrome + CDP
- [x] Persistencia de sesión en Keychain de macOS
- [x] Tools MCP de auth y logout
- [ ] Cliente HTTP base con bypass de DataDome (`curl-cffi`)
- [ ] Listado de reembolsos activos y resueltos
- [ ] Detalle de reembolsos resueltos (montos de bono, copago, costo)
- [ ] Lectura de PDFs subidos para detección de duplicados
- [ ] Resumen general de reembolsos
- [ ] Verificación de duplicados por folio SII / RUT prestador
- [ ] Subir nueva solicitud de reembolso

## Disclaimer

Este proyecto no está afiliado ni es aprobado por Isapre Esencial.
