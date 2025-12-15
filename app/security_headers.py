from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                def set_hdr(name: str, value: str):
                    headers[name.lower().encode()] = value.encode()

                # Clickjacking / Permissions-Policy.
                set_hdr("x-frame-options", "DENY")
                set_hdr("x-content-type-options", "nosniff")
                set_hdr(
                    "permissions-policy", "geolocation=(), microphone=(), camera=()"
                )

                # Site Isolation.
                set_hdr("cross-origin-opener-policy", "same-origin")
                set_hdr("cross-origin-embedder-policy", "require-corp")
                set_hdr("cross-origin-resource-policy", "same-origin")

                # CSP.
                set_hdr(
                    "content-security-policy",
                    "default-src 'self'; "
                    "img-src 'self' data:; "
                    "script-src 'self' https://cdn.jsdelivr.net; "
                    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none';",
                )

                set_hdr("cache-control", "no-store")
                message = {**message, "headers": [(k, v) for k, v in headers.items()]}
            await send(message)

        await self.app(scope, receive, send_wrapper)
