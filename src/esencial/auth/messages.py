"""User-facing Spanish messages for the auth flow."""

DIALOG_TITLE = "Isapre Esencial"

LOGIN_PROMPT = (
    "Completa el login en Chrome:\n"
    "RUT, contraseña, captcha y 2FA si corresponde.\n\n"
    "Haz clic en OK cuando estés en el dashboard."
)

SESSION_SAVED = "✅ Sesión guardada correctamente."

ERR_NO_CREDENTIALS = (
    "No se pudieron obtener las credenciales. ¿Llegaste al dashboard antes de hacer clic en OK?"
)
ERR_EXTRACT_SESSION = "Error extrayendo sesión:\n{error}"
