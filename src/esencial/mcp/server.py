"""MCP Server for Isapre Esencial reimbursements."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="esencial-reembolsos")


@mcp.tool()
def about() -> str:
    """Returns information about this MCP server."""
    return (
        "esencial-reembolsos-mcp: MCP server to query and manage "
        "Isapre Esencial reimbursements from any compatible MCP client."
    )


def main() -> None:
    mcp.run()
