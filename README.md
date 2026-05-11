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
