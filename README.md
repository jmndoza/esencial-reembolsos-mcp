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
| `list_refunds` | Lista solicitudes de reembolso (active / resolved) con paginación |
| `refund_detail` | Detalle completo de un reembolso resuelto (líneas, montos, prestador) |
| `list_documents` | Documentos (boletas/facturas) adjuntos en solicitudes activas y resueltas |
| `read_active_documents` | Descarga y extrae texto de los PDFs de solicitudes activas |
| `refunds_summary` | Totales rápidos de solicitudes activas y resueltas |

## Roadmap

- [x] Autenticación interactiva con Chrome + CDP
- [x] Persistencia de sesión en Keychain de macOS
- [x] Cliente HTTP base con bypass de DataDome (`curl-cffi`)
- [x] Listado y detalle de reembolsos (active / resolved)
- [x] Lectura de PDFs subidos para detección de duplicados
- [x] Resumen general de reembolsos
- [ ] Subir nueva solicitud de reembolso

## Disclaimer

Este proyecto no está afiliado ni es aprobado por Isapre Esencial. Usa la API interna de Esencial mediante ingeniería inversa, por lo que puede dejar de funcionar sin previo aviso.
