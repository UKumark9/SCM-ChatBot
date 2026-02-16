"""
Standalone login server for SCM Chatbot.
Runs on http://127.0.0.1:8080
Redirects to http://127.0.0.1:7860 after successful login.

Usage:
    python login_server.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from modules.auth_utils import authenticate, get_role, sign_user

app = FastAPI(title="SCM Chatbot Login")

CHATBOT_URL = "http://127.0.0.1:7860/"
LOGIN_URL   = "http://127.0.0.1:8000/"

# ── HTML Template ─────────────────────────────────────────────────────────────
def build_page(error: str = "", info: str = "") -> str:
    error_html = (
        f'<div class="error-box">'
        f'<svg viewBox="0 0 24 24" width="16" height="16"><circle cx="12" cy="12" r="10"/>'
        f'<line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
        f'{error}</div>'
        if error else ""
    )
    info_html = (
        f'<div class="info-box">'
        f'<svg viewBox="0 0 24 24" width="16" height="16"><circle cx="12" cy="12" r="10"/>'
        f'<line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
        f'{info}</div>'
        if info else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SCM Chatbot — Sign In</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0f172a;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}

    /* ── Animated background ── */
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 80% 50% at 20% 40%, rgba(99,102,241,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 60%, rgba(79,70,229,0.10) 0%, transparent 60%);
      pointer-events: none;
    }}

    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 20px;
      padding: 48px 44px;
      width: 100%;
      max-width: 420px;
      box-shadow:
        0 0 0 1px rgba(99,102,241,0.08),
        0 20px 60px rgba(0,0,0,0.5),
        0 4px 16px rgba(0,0,0,0.3);
      position: relative;
      animation: slideUp 0.4s ease;
    }}

    @keyframes slideUp {{
      from {{ opacity: 0; transform: translateY(24px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ── Logo ── */
    .logo {{
      width: 64px; height: 64px;
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      border-radius: 16px;
      display: flex; align-items: center; justify-content: center;
      margin: 0 auto 24px;
      font-size: 28px;
      box-shadow: 0 4px 20px rgba(99,102,241,0.4);
    }}

    h1 {{
      color: #f1f5f9;
      font-size: 1.6rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 6px;
    }}

    .subtitle {{
      color: #64748b;
      font-size: 0.875rem;
      text-align: center;
      margin-bottom: 36px;
    }}

    /* ── Form ── */
    .field {{
      margin-bottom: 20px;
    }}

    label {{
      display: block;
      color: #94a3b8;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}

    input {{
      width: 100%;
      background: #0f172a;
      border: 1.5px solid #334155;
      border-radius: 10px;
      padding: 12px 16px;
      color: #f1f5f9;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}

    input:focus {{
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
    }}

    input::placeholder {{ color: #475569; }}

    /* ── Error box ── */
    .error-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(239,68,68,0.12);
      border: 1px solid rgba(239,68,68,0.35);
      border-radius: 10px;
      padding: 12px 14px;
      color: #fca5a5;
      font-size: 0.875rem;
      margin-bottom: 20px;
      animation: shake 0.3s ease;
    }}

    .error-box svg {{ flex-shrink: 0; stroke: #ef4444; fill: none; stroke-width: 2; }}

    /* ── Info box (logout success) ── */
    .info-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(16,185,129,0.1);
      border: 1px solid rgba(16,185,129,0.3);
      border-radius: 10px;
      padding: 12px 14px;
      color: #6ee7b7;
      font-size: 0.875rem;
      margin-bottom: 16px;
    }}
    .info-box svg {{ flex-shrink: 0; stroke: #10b981; fill: none; stroke-width: 2; }}

    @keyframes shake {{
      0%,100% {{ transform: translateX(0); }}
      25%      {{ transform: translateX(-6px); }}
      75%      {{ transform: translateX(6px); }}
    }}

    /* ── Submit button ── */
    button {{
      width: 100%;
      padding: 13px;
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      border: none;
      border-radius: 10px;
      color: #fff;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      margin-top: 8px;
      transition: opacity 0.2s, transform 0.1s, box-shadow 0.2s;
      box-shadow: 0 4px 14px rgba(99,102,241,0.35);
      position: relative;
      overflow: hidden;
    }}

    button:hover  {{ opacity: 0.92; box-shadow: 0 6px 20px rgba(99,102,241,0.45); }}
    button:active {{ transform: scale(0.98); }}

    /* ── Hint ── */
    .hint {{
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid #1e293b;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .hint-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      background: #0f172a;
      border-radius: 8px;
      border: 1px solid #1e293b;
    }}

    .role-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 20px;
      min-width: 80px;
      justify-content: center;
    }}

    .badge-admin   {{ background: rgba(99,102,241,0.2); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }}
    .badge-analyst {{ background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.25); }}

    .creds {{
      color: #64748b;
      font-size: 0.8rem;
      font-family: 'SF Mono', 'Fira Code', monospace;
    }}

    .creds strong {{ color: #94a3b8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">&#128736;</div>
    <h1>SCM Chatbot</h1>
    <p class="subtitle">Supply Chain Management</p>

    {info_html}
    {error_html}

    <form method="POST" action="/login">
      <div class="field">
        <label for="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          placeholder="Enter your username"
          autocomplete="username"
          autofocus
          required
        >
      </div>

      <div class="field">
        <label for="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          placeholder="Enter your password"
          autocomplete="current-password"
          required
        >
      </div>

      <button type="submit">Sign In &rarr;</button>
    </form>

    <div class="hint">
      <div class="hint-row">
        <span class="role-badge badge-admin">&#x1F512; Admin</span>
        <span class="creds"><strong>admin</strong> / admin123</span>
      </div>
      <div class="hint-row">
        <span class="role-badge badge-analyst">&#x1F4CA; Analyst</span>
        <span class="creds"><strong>analyst</strong> / analyst123</span>
      </div>
    </div>
  </div>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return build_page()


@app.post("/login")
async def handle_login(
    username: str = Form(...),
    password: str = Form(...),
):
    uname = username.strip().lower()
    if authenticate(uname, password):
        role = get_role(uname)
        sig  = sign_user(uname, role)
        url  = f"{CHATBOT_URL}?user={uname}&role={role}&sig={sig}"
        return RedirectResponse(url=url, status_code=303)
    return HTMLResponse(
        content=build_page(error="Invalid username or password. Please try again."),
        status_code=401,
    )


@app.get("/logout", response_class=HTMLResponse)
async def logout():
    return build_page(info="You have been logged out successfully.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  SCM Chatbot Login Server")
    print("=" * 55)
    print(f"  Login page : http://127.0.0.1:8000/")
    print(f"  Redirects  : {CHATBOT_URL}")
    print(f"\n  Users:")
    print(f"    admin   / admin123   (Administrator)")
    print(f"    analyst / analyst123 (Data Analyst)")
    print("=" * 55 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
