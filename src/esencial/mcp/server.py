"""MCP Server for Isapre Esencial reimbursements."""

from mcp.server.fastmcp import FastMCP

from esencial.auth.login import login
from esencial.auth.session import clear_session
from esencial.mcp.messages import ABOUT, AUTH_FAILED, AUTH_SUCCESS, LOGOUT_SUCCESS

mcp = FastMCP(name="esencial-reembolsos")


@mcp.tool()
def about() -> str:
    """Return information about this MCP server."""
    return ABOUT


@mcp.tool()
def auth() -> str:
    """Open Chrome for the user to log in to Isapre Esencial."""
    return AUTH_SUCCESS if login() else AUTH_FAILED


@mcp.tool()
def logout() -> str:
    """Delete the locally saved session."""
    clear_session()
    return LOGOUT_SUCCESS


def main() -> None:
    mcp.run()
