""" وب‌سرور FastAPI: مسیر دانلود مستقیم فایل‌ها + پنل مدیریت ساده. """
import os
import time
import secrets
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response

from config import LINK_TTL_HOURS, PUBLIC_BASE_URL, ADMIN_PANEL_USERNAME, ADMIN_PANEL_PASSWORD
from utils.helpers import format_size
from web import store
from web.settings import get_settings, update_settings
from web.auth import require_admin, create_session

app = FastAPI(title="TeleTube", docs_url=None, redoc_url=None)

FAILED_ATTEMPTS = {}

@app.get("/logo.svg")
async def get_custom_logo():
    """مسیر خواندن لوگوی اختصاصی کاربر از پوشه مدیا"""
    logo_path = "media/logo.svg"
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/svg+xml")
    # در صورتی که فایل پیدا نشد یک پاسخ خالی برمی‌گرداند تا ارور ندهد
    return Response(content=b"", media_type="image/svg+xml")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None, mins: str = None):
    error_msg = ""
    if error == "invalid":
        error_msg = '<div class="mt-3 p-2 rounded" style="background: rgba(244, 63, 94, 0.2); border: 1px solid rgba(244, 63, 94, 0.4); color: #fb7185; font-size: 0.85rem;">نام کاربری یا رمز عبور اشتباه است!</div>'
    elif error == "locked":
        error_msg = f'<div class="mt-3 p-2 rounded" style="background: rgba(244, 63, 94, 0.2); border: 1px solid rgba(244, 63, 94, 0.4); color: #fb7185; font-size: 0.85rem;"><i class="bi bi-shield-lock-fill me-1"></i> دسترسی شما مسدود شد. لطفاً {mins} دقیقه دیگر تلاش کنید.</div>'
        
    html = f"""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TeleTube Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            :root {{ --glass-bg: rgba(30, 41, 59, 0.4); --glass-border: rgba(255, 255, 255, 0.08); --glass-blur: blur(16px); --accent-color: #38bdf8; }}
            body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
            .bg-orb {{ position: absolute; border-radius: 50%; filter: blur(100px); z-index: -1; animation: float 12s infinite ease-in-out alternate; }}
            .orb-1 {{ width: 400px; height: 400px; background: rgba(99, 102, 241, 0.3); top: -10%; left: -10%; }}
            .orb-2 {{ width: 500px; height: 500px; background: rgba(236, 72, 153, 0.2); bottom: -20%; right: -10%; animation-delay: -5s; }}
            @keyframes float {{ 0% {{ transform: translateY(0) scale(1); }} 100% {{ transform: translateY(-40px) scale(1.1); }} }}
            .glass {{ background: var(--glass-bg); backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); width: 100%; max-width: 380px; padding: 40px; position: relative; z-index: 10; }}
            .form-control {{ background: rgba(0, 0, 0, 0.2) !important; border: 1px solid var(--glass-border) !important; color: #f8fafc !important; border-radius: 12px; padding: 12px 15px; }}
            .form-control:focus {{ box-shadow: 0 0 0 0.25rem rgba(56, 189, 248, 0.2) !important; border-color: var(--accent-color) !important; }}
            .btn-glass-primary {{ background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: var(--accent-color); transition: all 0.3s; border-radius: 12px; font-weight: 600; }}
            .btn-glass-primary:hover {{ background: rgba(56, 189, 248, 0.3); color: #fff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }}
        </style>
    </head>
    <body>
        <div class="bg-orb orb-1"></div>
        <div class="bg-orb orb-2"></div>
        <div class="glass text-center">
            <img src="/logo.svg" alt="TeleTube Logo" style="width: 70px; height: 70px; object-fit: contain; filter: drop-shadow(0 0 8px rgba(255,255,255,0.15));">
            <h4 class="mt-3 mb-4 fw-bold" style="letter-spacing: 1px;">TELETUBE <span class="fw-light fs-6" style="color: #10b981;">LOGIN</span></h4>
            <form action="/login" method="post">
                <div class="mb-3 text-start">
                    <label class="form-label text-info small fw-bold">Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-4 text-start">
                    <label class="form-label text-info small fw-bold">Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-glass-primary w-100 py-3 mt-2">
                    <i class="bi bi-box-arrow-in-right me-2"></i> Sign In
                </button>
                {error_msg}
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/login")
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host
    now = time.time()
    
    ip_record = FAILED_ATTEMPTS.get(client_ip, {"count": 0, "lock_until": 0})
    if now < ip_record["lock_until"]:
        remaining = int((ip_record["lock_until"] - now) / 60) or 1
        return RedirectResponse(url=f"/login?error=locked&mins={remaining}", status_code=303)
        
    correct_username = secrets.compare_digest(username, ADMIN_PANEL_USERNAME)
    correct_password = secrets.compare_digest(password, ADMIN_PANEL_PASSWORD)
    
    if correct_username and correct_password:
        if client_ip in FAILED_ATTEMPTS:
            del FAILED_ATTEMPTS[client_ip]
        token = create_session()
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="teletube_session", value=token, httponly=True, max_age=86400)
        return response
        
    ip_record["count"] += 1
    if ip_record["count"] >= 5:
        ip_record["lock_until"] = now + 900
        FAILED_ATTEMPTS[client_ip] = ip_record
        return RedirectResponse(url="/login?error=locked&mins=15", status_code=303)
        
    FAILED_ATTEMPTS[client_ip] = ip_record
    return RedirectResponse(url="/login?error=invalid", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("teletube_session")
    import web.auth
    web.auth._ACTIVE_SESSION = None
    return response

@app.get("/")
async def root():
    return {"service": "TeleTube", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/files/{token}")
async def download_file(token: str):
    entry = store.get_link(token)
    if not entry or entry.get("is_deleted"):
        raise HTTPException(status_code=404, detail="لینک پیدا نشد یا فایل از سرور حذف شده است")
    
    if not os.path.exists(entry["file_path"]):
        raise HTTPException(status_code=404, detail="فایل دیگه روی سرور موجود نیست")
        
    store.record_download(token)
    filename = f"{entry['title']}.mp4"
    return FileResponse(entry["file_path"], media_type="video/mp4", filename=filename)

@app.get("/thumbs/{token}")
async def get_thumbnail(token: str):
    entry = store.get_link(token)
    if entry and entry.get("thumb_path") and os.path.exists(entry["thumb_path"]):
        return FileResponse(entry["thumb_path"])
    return Response(content=b"", media_type="image/jpeg")

def _fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def _render_admin_page(settings: dict, links: list, base_url: str) -> str:
    checked_direct = "checked" if settings.get("enable_direct_links", True) else ""
    checked_channel = "checked" if settings.get("enable_channel_delivery", True) else ""
    checked_urldl = "checked" if settings.get("enable_urldl", False) else ""
    checked_anim = "checked" if settings.get("enable_animation", True) else ""
    
    expire_time_ms = settings.get("expire_time", time.time() + (30 * 24 * 3600) - 3600) * 1000
    links.sort(key=lambda x: (x.get('is_deleted', False), -x['created_at']))
    
    days_options = "".join([f'<option value="{i}" {"selected" if i==30 else ""}>{i}</option>' for i in range(61)])
    hours_options = "".join([f'<option value="{i}">{i}</option>' for i in range(24)])
    
    cards_html = ""
    for entry in links:
        token = entry['token']
        dl_link = f"{base_url}/files/{token}" if base_url else f"/files/{token}"
        urldl_link = entry.get('urldl_link') or ''
        tg_link = entry.get('tg_link') or ''
        is_deleted = entry.get('is_deleted', False)
        is_del_js = 'true' if is_deleted else 'false'
        
        safe_title = entry['title'].replace("'", "\\'").replace('"', '&quot;')
        
        if is_deleted:
            badge_html = '<span class="position-absolute top-0 start-0 m-2 badge bg-danger opacity-75" style="z-index:2;" data-en="Deleted" data-fa="حذف شده">Deleted</span>'
            thumb_html = '<div class="w-100 h-100 d-flex justify-content-center align-items-center" style="background: rgba(0,0,0,0.6); position:absolute; top:0; left:0;"><i class="bi bi-trash3 text-secondary" style="font-size: 3rem;"></i></div>'
        else:
            badge_html = '<span class="position-absolute top-0 start-0 m-2 badge bg-success opacity-75" style="z-index:2;" data-en="Active" data-fa="موجود">Active</span>'
            thumb_html = f'<img src="/thumbs/{token}" alt="">'
        
        cards_html += f'''
        <div class="col video-col" data-created="{entry['created_at']}" data-deleted="{is_del_js}">
            <div class="glass video-card h-100" onclick="showModal('{token}', '{safe_title}', '{dl_link}', '{urldl_link}', '{tg_link}', {entry['created_at']}, {entry['expires_at']}, {is_del_js})">
                <div class="thumb-container">
                    {badge_html}
                    {thumb_html}
                    <div class="play-overlay"><i class="bi bi-play-circle-fill"></i></div>
                </div>
                <div class="card-body p-3">
                    <h6 class="video-title" title="{entry['title']}">{entry['title']}</h6>
                    <div class="video-meta mt-3">
                        <div class="d-flex justify-content-between mb-1">
                            <span><i class="bi bi-hdd-fill me-1"></i> {format_size(entry['size_bytes']) or '-'}</span>
                            <span><i class="bi bi-cloud-arrow-down-fill me-1"></i> {entry['downloads']}</span>
                        </div>
                        <div><i class="bi bi-calendar3 me-1"></i> <span data-en="Created:" data-fa="ساخت:">Created:</span> {_fmt_time(entry['created_at'])}</div>
                    </div>
                </div>
            </div>
        </div>
        '''
        
    if not cards_html:
        cards_html = '''
        <div class="col-12 text-center my-5">
            <div class="glass p-5 d-inline-block" style="border-radius: 24px;">
                <i class="bi bi-camera-reels text-muted" style="font-size: 4rem;"></i>
                <h5 class="mt-3 text-muted" data-en="No videos in archive" data-fa="هیچ ویدیویی در آرشیو وجود ندارد">No videos in archive</h5>
            </div>
        </div>'''

    return f"""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TeleTube Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" id="bs-css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            :root {{
                --glass-bg: rgba(30, 41, 59, 0.4);
                --glass-border: rgba(255, 255, 255, 0.08);
                --glass-blur: blur(16px);
                --accent-color: #38bdf8;
            }}
            body {{
                background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                min-height: 100vh; overflow-x: hidden; position: relative; transition: direction 0.3s;
            }}
            body[dir="ltr"] {{ text-align: left; }}
            body[dir="rtl"] {{ text-align: right; }}

            .main-content {{ position: relative; z-index: 10; }}

            .fixed-nav-container {{
                position: relative; width: 100%; height: 40px;
                display: flex; align-items: center; justify-content: space-between;
                direction: ltr !important; 
            }}
            .fixed-brand, .fixed-lang {{ direction: ltr; }}

            .bg-orb {{ position: fixed; border-radius: 50%; filter: blur(100px); z-index: -1; animation: float 12s infinite ease-in-out alternate; }}
            .orb-1 {{ width: 400px; height: 400px; background: rgba(99, 102, 241, 0.3); top: -10%; left: -10%; }}
            .orb-2 {{ width: 500px; height: 500px; background: rgba(236, 72, 153, 0.2); bottom: -20%; right: -10%; animation-delay: -5s; }}
            .orb-3 {{ width: 350px; height: 350px; background: rgba(56, 189, 248, 0.2); top: 30%; left: 40%; animation-duration: 18s; }}

            @keyframes float {{ 0% {{ transform: translateY(0) scale(1); }} 100% {{ transform: translateY(-40px) scale(1.1); }} }}

            @keyframes rocket-pulse {{
                0% {{ transform: scale(1) translateY(0); filter: drop-shadow(0 0 2px rgba(245, 158, 11, 0.4)); }}
                50% {{ transform: scale(1.15) translateY(-2px); filter: drop-shadow(0 0 12px rgba(245, 158, 11, 0.9)); }}
                100% {{ transform: scale(1) translateY(0); filter: drop-shadow(0 0 2px rgba(245, 158, 11, 0.4)); }}
            }}
            .rocket-animated {{ animation: rocket-pulse 2s infinite ease-in-out; display: inline-block; }}

            .space-entity {{
                position: fixed;
                pointer-events: none;
                opacity: 0;
                transition: left 1s ease-in-out, top 1s ease-in-out, transform 0.4s ease, opacity 0.5s;
            }}
            .projectile {{
                transition: left 0.4s linear, top 0.4s linear, opacity 0.2s;
                transform-origin: center center;
            }}
            .pixel-particle {{
                position: fixed; width: 8px; height: 8px;
                pointer-events: none;
                transition: transform 0.5s ease-out, opacity 0.5s ease-out;
                box-shadow: 0 0 8px rgba(255,255,255,0.4);
            }}

            .glass {{ background: var(--glass-bg); backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }}
            .navbar-glass {{ background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border-bottom: 1px solid var(--glass-border); }}
            .glass-dropdown {{ background: rgba(15, 23, 42, 0.9) !important; backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 12px; }}
            .glass-dropdown .dropdown-item:hover {{ background: rgba(56, 189, 248, 0.2); color: #fff; }}

            .timer-widget {{ background: linear-gradient(135deg, rgba(30,41,59,0.7) 0%, rgba(15,23,42,0.8) 100%); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 20px; }}

            .video-card {{ cursor: pointer; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s; display: flex; flex-direction: column; position: relative; overflow: hidden; }}
            .video-card:hover {{ transform: translateY(-8px); background: rgba(30, 41, 59, 0.6); border-color: rgba(56, 189, 248, 0.3); }}
            .thumb-container {{ position: relative; width: 100%; padding-top: 56.25%; background: #000; overflow: hidden; border-bottom: 1px solid var(--glass-border); }}
            .thumb-container img {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.85; transition: opacity 0.3s, transform 0.5s; }}
            .video-card:hover .thumb-container img {{ opacity: 1; transform: scale(1.05); }}
            
            .play-overlay {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 3rem; color: rgba(255, 255, 255, 0.7); opacity: 0; transition: opacity 0.3s, transform 0.3s; z-index:3; }}
            .video-card:hover .play-overlay {{ opacity: 1; transform: translate(-50%, -50%) scale(1.1); }}

            .video-title {{ font-size: 0.95rem; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-weight: 600; color: #f1f5f9; }}
            .video-meta {{ font-size: 0.8rem; color: #94a3b8; }}
            .video-meta i {{ color: var(--accent-color); }}

            .form-control, .form-select, .input-group-text {{ background: rgba(0, 0, 0, 0.2) !important; border: 1px solid var(--glass-border) !important; color: #f8fafc !important; }}
            .form-control:focus, .form-select:focus {{ box-shadow: 0 0 0 0.25rem rgba(56, 189, 248, 0.2) !important; border-color: var(--accent-color) !important; }}
            .form-select option {{ background: #0f172a; color: #f8fafc; }}

            .modal-content {{ background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 24px; color: #e2e8f0; }}
            .modal-header {{ border-bottom: 1px solid var(--glass-border); }}
            .btn-close {{ filter: invert(1); opacity: 0.7; }}
            .btn-close:hover {{ opacity: 1; }}

            .water-btn {{ position: relative; overflow: hidden; background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.3); color: var(--accent-color); border-radius: 12px; user-select: none; touch-action: none; cursor: pointer; transition: transform 0.1s; }}
            .water-btn:active {{ transform: scale(0.98); }}
            .water-fill {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: rgba(56, 189, 248, 0.6); z-index: 1; transition: height 0.05s linear; }}
            .water-text {{ position: relative; z-index: 2; font-weight: 600; }}

            .btn-glass-primary {{ background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: var(--accent-color); transition: all 0.3s; border-radius: 12px; }}
            .btn-glass-primary:hover {{ background: rgba(56, 189, 248, 0.3); color: #fff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }}
            
            .btn-glass-danger {{ background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); color: #fb7185; transition: all 0.3s; border-radius: 12px; }}
            .btn-glass-danger:hover {{ background: rgba(244, 63, 94, 0.3); color: #fff; box-shadow: 0 0 15px rgba(244, 63, 94, 0.3); }}

            .copy-btn {{ background: rgba(255, 255, 255, 0.05) !important; color: #cbd5e1 !important; border-color: var(--glass-border) !important; transition: background 0.2s; }}
            .copy-btn:hover {{ background: rgba(255, 255, 255, 0.15) !important; color: #fff !important; }}

            .form-switch .form-check-input {{ background-color: rgba(255, 255, 255, 0.2); border-color: rgba(255, 255, 255, 0.1); cursor: pointer; float: none; margin-top: 0; width: 2.5em; height: 1.25em; }}
            .form-switch .form-check-input:checked {{ background-color: var(--accent-color); border-color: var(--accent-color); }}

        </style>
    </head>
    <body>

    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <div class="main-content">
        <nav class="navbar navbar-glass sticky-top py-3 mb-4">
            <div class="container fixed-nav-container">
                <div class="fixed-brand">
                    <a class="navbar-brand fw-bold text-white d-flex align-items-center m-0" href="#">
                        <img src="/logo.svg" alt="TeleTube Logo" style="width: 32px; height: 32px; object-fit: contain; filter: drop-shadow(0 0 5px rgba(255,255,255,0.2));" class="me-3">
                        <span style="letter-spacing: 1px;">TELETUBE <span class="fw-light" style="color: #10b981;">DASHBOARD</span></span>
                    </a>
                </div>
                <div class="fixed-lang d-flex align-items-center gap-2">
                    <button id="langBtn" class="btn btn-outline-info btn-sm rounded-pill px-3" onclick="toggleLanguage()">FA</button>
                    <a href="/logout" class="btn btn-outline-danger btn-sm rounded-pill px-3" title="Logout">
                        <i class="bi bi-power"></i>
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mb-5 pb-5">
        
            <!-- تایمر Railway Widget -->
            <div class="glass timer-widget p-4 mb-5 shadow-sm d-flex flex-column flex-md-row justify-content-between align-items-center">
                <div class="d-flex align-items-center mb-3 mb-md-0">
                    <div class="p-3 rounded-circle me-3 ms-2" style="background: rgba(245, 158, 11, 0.1);">
                        <i class="bi bi-rocket-takeoff fs-2 text-warning rocket-animated"></i>
                    </div>
                    <div>
                        <h5 class="mb-1 fw-bold text-white" data-en="Server Plan Expiration" data-fa="زمان پایان پلن سرور">Server Plan Expiration</h5>
                        <div class="d-flex align-items-center">
                            <span class="text-info fs-6" id="railwayTimer" style="letter-spacing: 0.5px;"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <button type="button" class="btn btn-glass-primary px-4 py-2 rounded-pill" data-bs-toggle="modal" data-bs-target="#planModal">
                        <i class="bi bi-calendar2-check me-2"></i> <span data-en="Adjust Time" data-fa="تنظیم زمان">Adjust Time</span>
                    </button>
                </div>
            </div>

            <div class="row">
                <!-- Settings Panel -->
                <div class="col-lg-6 mb-4">
                    <div class="glass p-4 h-100 d-flex flex-column">
                        <h5 class="mb-4 text-white"><i class="bi bi-sliders text-info me-2"></i> <span data-en="System Configuration" data-fa="پیکربندی سیستم">System Configuration</span></h5>
                        <form action="/admin/settings" method="post" id="settingsForm" class="flex-grow-1 d-flex flex-column">
                            
                            <div class="d-flex justify-content-between align-items-center py-3 border-bottom border-secondary border-opacity-10 mb-2">
                                <label class="form-check-label fs-6 mb-0" for="c1" data-en="Direct Server Link" data-fa="لینک مستقیم سرور">Direct Server Link</label>
                                <div class="form-check form-switch m-0 p-0 d-flex align-items-center">
                                    <input class="form-check-input m-0" type="checkbox" name="enable_direct_links" id="c1" value="true" {checked_direct}>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between align-items-center py-3 border-bottom border-secondary border-opacity-10 mb-2">
                                <label class="form-check-label fs-6 mb-0" for="c2" data-en="Upload to Telegram Channel" data-fa="آپلود در کانال تلگرام">Upload to Telegram Channel</label>
                                <div class="form-check form-switch m-0 p-0 d-flex align-items-center">
                                    <input class="form-check-input m-0" type="checkbox" name="enable_channel_delivery" id="c2" value="true" {checked_channel}>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center py-3 border-bottom border-secondary border-opacity-10 mb-2">
                                <label class="form-check-label fs-6 mb-0" for="c3" data-en="Internal urldl.ir Route" data-fa="مسیر داخلی urldl.ir">Internal urldl.ir Route</label>
                                <div class="form-check form-switch m-0 p-0 d-flex align-items-center">
                                    <input class="form-check-input m-0" type="checkbox" name="enable_urldl" id="c3" value="true" {checked_urldl}>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between align-items-center py-3 mb-3">
                                <label class="form-check-label fs-6 mb-0 text-warning" for="c_anim" data-en="Spaceship Animation " data-fa="انیمیشن نبرد فضایی ">Spaceship Animation (Easter Egg)</label>
                                <div class="form-check form-switch m-0 p-0 d-flex align-items-center">
                                    <input class="form-check-input m-0" type="checkbox" name="enable_animation" id="c_anim" value="true" {checked_anim}>
                                </div>
                            </div>
                            
                            <div class="mt-auto pt-4 border-top border-secondary border-opacity-25">
                                <button type="button" class="btn water-btn w-100 py-3" id="holdBtn">
                                    <div class="water-fill" id="waterFill"></div>
                                    <span class="water-text">
                                        <i class="bi bi-hdd-network me-2"></i> 
                                        <span data-en="Hold to Apply Settings" data-fa="برای اعمال تنظیمات نگه دارید">Hold to Apply Settings</span>
                                    </span>
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Bot Control Panel -->
                <div class="col-lg-6 mb-4">
                    <div class="glass p-4 h-100">
                        <h5 class="mb-4 text-white"><i class="bi bi-robot text-primary me-2"></i> <span data-en="Telegram Bot Control" data-fa="کنترل ربات تلگرام">Telegram Bot Control</span></h5>
                        <div class="d-flex flex-column justify-content-center align-items-center h-75 opacity-50">
                            <i class="bi bi-tools fs-1 mb-2"></i>
                            <span data-en="Features will be added soon..." data-fa="امکانات این بخش به زودی اضافه خواهد شد...">Features will be added soon...</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-3 mb-4 border-bottom border-secondary border-opacity-25 pb-3">
                <h4 class="m-0 text-white"><i class="bi bi-archive me-2 text-info"></i> <span data-en="Video Archive" data-fa="آرشیو ویدیوها">Video Archive</span></h4>
                
                <div class="dropdown">
                    <button class="btn btn-outline-info dropdown-toggle" style="border-radius: 12px;" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi bi-filter"></i> <span id="currentFilterLabel" data-en="All Downloads" data-fa="همه دانلودها">All Downloads</span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-dark glass-dropdown shadow-lg">
                        <li><a class="dropdown-item" href="#" onclick="filterVideos('all', this)" data-en="All Downloads" data-fa="همه دانلودها">All Downloads</a></li>
                        <li><a class="dropdown-item" href="#" onclick="filterVideos('today', this)" data-en="Today" data-fa="امروز">Today</a></li>
                        <li><a class="dropdown-item" href="#" onclick="filterVideos('week', this)" data-en="This Week" data-fa="این هفته">This Week</a></li>
                        <li><a class="dropdown-item" href="#" onclick="filterVideos('month', this)" data-en="This Month" data-fa="این ماه">This Month</a></li>
                        <li><hr class="dropdown-divider border-secondary"></li>
                        <li><a class="dropdown-item text-danger" href="#" onclick="filterVideos('deleted', this)" data-en="Deleted" data-fa="حذف شده‌ها">Deleted</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4" id="videoGrid">
                {cards_html}
            </div>
        </div>
    </div> 

    <!-- Modal for Adjusting Plan Time -->
    <div class="modal fade" id="planModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-sm" style="z-index: 1055;">
            <div class="modal-content shadow-lg">
                <div class="modal-header border-0 pb-0 mt-2 px-4">
                    <h6 class="modal-title fw-bold text-white w-100 pe-3" dir="auto">
                        <i class="bi bi-clock-history text-warning me-2"></i>
                        <span data-en="Set Plan Duration" data-fa="تنظیم مدت زمان پلن">Set Plan Duration</span>
                    </h6>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body px-4 pb-4 mt-3">
                    <div class="mb-4">
                        <label class="form-label text-info small fw-bold mb-2" data-en="Quick Presets" data-fa="گزینه‌های سریع">Quick Presets</label>
                        <div class="d-flex flex-wrap gap-2">
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="submitQuickPlan(29, 12)" data-en="29d 12h" data-fa="۲۹ روز و ۱۲ ساعت">29d 12h</button>
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="submitQuickPlan(29, 0)" data-en="29 Days" data-fa="۲۹ روز">29 Days</button>
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="submitQuickPlan(25, 0)" data-en="25 Days" data-fa="۲۵ روز">25 Days</button>
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="submitQuickPlan(15, 0)" data-en="15 Days" data-fa="۱۵ روز">15 Days</button>
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="submitQuickPlan(10, 0)" data-en="10 Days" data-fa="۱۰ روز">10 Days</button>
                        </div>
                    </div>
                    
                    <form action="/admin/plan/update" method="post" id="planForm">
                        <div class="row g-3 mb-4">
                            <div class="col-6">
                                <label class="form-label text-info small fw-bold" data-en="Days" data-fa="روز">Days</label>
                                <select name="days" class="form-select text-center fw-bold" dir="ltr" id="selectDays">
                                    {days_options}
                                </select>
                            </div>
                            <div class="col-6">
                                <label class="form-label text-info small fw-bold" data-en="Hours" data-fa="ساعت">Hours</label>
                                <select name="hours" class="form-select text-center fw-bold" dir="ltr" id="selectHours">
                                    {hours_options}
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-glass-primary w-100 py-2">
                            <i class="bi bi-check2-circle me-2"></i> <span data-en="Apply Time" data-fa="اعمال زمان">Apply Time</span>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for Video Links -->
    <div class="modal fade" id="linkModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" style="z-index: 1055;">
            <div class="modal-content shadow-lg">
                <div class="modal-header border-0 pb-0 mt-2 px-4">
                    <h5 class="modal-title fw-bold text-truncate w-100 pe-3" id="modalTitle" dir="auto">Video Title</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body px-4 pb-4 mt-3">
                    
                    <div class="mb-4">
                        <div class="d-flex justify-content-between align-items-end mb-2">
                            <label class="form-label text-info small fw-bold mb-0"><i class="bi bi-globe2"></i> <span data-en="Direct Server Link" data-fa="لینک مستقیم سرور">Direct Server Link</span></label>
                            <span id="modalDirectTime" class="badge"></span>
                        </div>
                        <div class="input-group">
                            <input type="text" class="form-control text-start" id="modalDirect" readonly dir="ltr">
                            <button class="btn copy-btn px-3" type="button" onclick="copyToClipboard('modalDirect')"><i class="bi bi-clipboard"></i></button>
                        </div>
                    </div>

                    <div class="mb-4" id="urldlBox">
                        <div class="d-flex justify-content-between align-items-end mb-2">
                            <label class="form-label text-info small fw-bold mb-0"><i class="bi bi-lightning-charge-fill text-warning"></i> <span data-en="Internal Traffic (urldl)" data-fa="ترافیک داخلی (urldl)">Internal Traffic (urldl)</span></label>
                            <span id="modalUrldlTime" class="badge"></span>
                        </div>
                        <div class="input-group">
                            <input type="text" class="form-control text-start" id="modalUrldl" readonly dir="ltr">
                            <button class="btn copy-btn px-3" type="button" onclick="copyToClipboard('modalUrldl')"><i class="bi bi-clipboard"></i></button>
                        </div>
                    </div>

                    <div class="mb-5" id="tgBox">
                        <div class="d-flex justify-content-between align-items-end mb-2">
                            <label class="form-label text-info small fw-bold mb-0"><i class="bi bi-telegram text-primary"></i> <span data-en="Telegram Post" data-fa="پست ذخیره تلگرام">Telegram Post</span></label>
                            <span id="modalTgTime" class="badge"></span>
                        </div>
                        <div class="input-group">
                            <input type="text" class="form-control text-start" id="modalTg" readonly dir="ltr">
                            <button class="btn copy-btn px-3" type="button" onclick="copyToClipboard('modalTg')"><i class="bi bi-clipboard"></i></button>
                        </div>
                    </div>

                    <form id="deleteForm" method="post" action="">
                        <button type="submit" class="btn btn-glass-danger w-100 py-2 fs-6">
                            <i class="bi bi-trash3-fill me-2"></i> <span data-en="Delete File (Keep in Archive)" data-fa="حذف فایل از سرور (باقی‌ماندن در آرشیو)">Delete File (Keep in Archive)</span>
                        </button>
                    </form>

                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Custom Timer Logic 
        const expireTimeMs = {expire_time_ms};
        let currentLang = localStorage.getItem('teletube_lang') || 'en';

        function updateRailwayTimer() {{
            const now = Date.now();
            const diff = expireTimeMs - now;
            
            if (diff <= 0) {{
                const msg = currentLang === 'fa' ? 'پلن منقضی شده است' : 'Plan Expired';
                document.getElementById('railwayTimer').innerText = msg;
                document.getElementById('railwayTimer').className = 'text-danger fw-bold fs-6';
                return;
            }}
            
            const d = Math.floor(diff / (1000 * 60 * 60 * 24));
            const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const m = Math.floor((diff / 1000 / 60) % 60);
            
            const msg = currentLang === 'fa' 
                ? `${{d}} روز و ${{h}} ساعت و ${{m}} دقیقه دیگر` 
                : `${{d}}d ${{h}}h ${{m}}m remaining`;
                
            document.getElementById('railwayTimer').innerText = msg;
        }}
        
        updateRailwayTimer();
        setInterval(updateRailwayTimer, 60000);

        // Language Toggle System
        function applyLanguage() {{
            document.body.setAttribute('dir', currentLang === 'en' ? 'ltr' : 'rtl');
            document.getElementById('langBtn').innerText = currentLang === 'en' ? 'FA' : 'EN';
            
            const bsLink = document.getElementById('bs-css');
            if(currentLang === 'fa') {{
                bsLink.href = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css";
            }} else {{
                bsLink.href = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css";
            }}

            document.querySelectorAll('[data-en]').forEach(el => {{
                el.innerText = el.getAttribute(`data-${{currentLang}}`);
            }});
            
            updateRailwayTimer();
        }}

        function toggleLanguage() {{
            currentLang = currentLang === 'en' ? 'fa' : 'en';
            localStorage.setItem('teletube_lang', currentLang);
            applyLanguage();
        }}
        
        applyLanguage();

        // ----------------------------------------------------
        // انیمیشن سفینه فضایی (SVG + Pixel Explosion) 🚀
        // ----------------------------------------------------
        const ytSvg = `<svg width="80" height="80" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="ytGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#ff4b4b" /><stop offset="100%" stop-color="#b91c1c" />
            </linearGradient>
            <linearGradient id="glassGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#bae6fd" /><stop offset="100%" stop-color="#0284c7" />
            </linearGradient>
          </defs>
          <path d="M 45 90 Q 60 120 75 90 Z" fill="#f59e0b">
            <animate attributeName="d" values="M 45 90 Q 60 120 75 90 Z; M 48 90 Q 60 105 72 90 Z; M 45 90 Q 60 120 75 90 Z" dur="0.4s" repeatCount="indefinite"/>
          </path>
          <path d="M 60 10 L 110 80 L 80 85 L 60 65 L 40 85 L 10 80 Z" fill="url(#ytGrad)" />
          <ellipse cx="60" cy="55" rx="20" ry="40" fill="#e2e8f0" />
          <ellipse cx="60" cy="55" rx="14" ry="38" fill="#f8fafc" />
          <ellipse cx="60" cy="35" rx="10" ry="15" fill="url(#glassGrad1)" />
          <path d="M 54 30 Q 60 25 66 30" stroke="white" fill="transparent" opacity="0.6" />
          <g transform="translate(42, 57) scale(1.5)">
            <rect width="24" height="16" rx="4" fill="#ff0000" />
            <polygon points="9,4 9,12 16,8" fill="white" />
          </g>
        </svg>`;

        const tgSvg = `<svg width="80" height="80" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="tgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#60a5fa" /><stop offset="100%" stop-color="#1d4ed8" />
            </linearGradient>
            <linearGradient id="glassGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#bae6fd" /><stop offset="100%" stop-color="#0284c7" />
            </linearGradient>
          </defs>
          <path d="M 40 85 Q 60 115 80 85 Z" fill="#0ea5e9">
            <animate attributeName="d" values="M 40 85 Q 60 115 80 85 Z; M 45 85 Q 60 100 75 85 Z; M 40 85 Q 60 115 80 85 Z" dur="0.4s" repeatCount="indefinite"/>
          </path>
          <path d="M 15 60 C 15 30 105 30 105 60 C 120 80 80 90 60 90 C 40 90 0 80 15 60 Z" fill="url(#tgGrad)" />
          <ellipse cx="60" cy="60" rx="35" ry="25" fill="#cbd5e1" />
          <ellipse cx="60" cy="58" rx="30" ry="20" fill="#f1f5f9" />
          <path d="M 35 55 C 35 30 85 30 85 55 Z" fill="url(#glassGrad2)" />
          <g transform="translate(39, 53) scale(1.5)">
            <circle cx="14" cy="14" r="14" fill="#0088cc" />
            <path d="M 6 14 L 22 7 L 17 20 L 13 16 L 11 20 L 10 16 Z" fill="white" />
          </g>
        </svg>`;

        const bulletSvg = `<svg width="40" height="80" viewBox="0 0 40 80" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="trailGrad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" stop-color="#39ff14" stop-opacity="1" />
              <stop offset="100%" stop-color="#39ff14" stop-opacity="0" />
            </linearGradient>
          </defs>
          <g filter="url(#glow)">
              <!-- دنباله سبز -->
              <rect x="16" y="45" width="8" height="35" fill="url(#trailGrad)" rx="4"/>
              <!-- آیکون دانلود -->
              <circle cx="20" cy="15" r="8" fill="#39ff14" />
              <path d="M 16 15 L 24 15 L 24 40 L 30 40 L 20 55 L 10 40 L 16 40 Z" fill="#4ade80" />
              <path d="M 6 50 L 6 60 L 34 60 L 34 50" stroke="#16a34a" stroke-width="4" fill="none" stroke-linecap="round"/>
          </g>
        </svg>`;

        function triggerSpaceBattle() {{
            const animCheckbox = document.getElementById('c_anim');
            if (!animCheckbox || !animCheckbox.checked) return;

            const zLayer = Math.random() > 0.7 ? '9999' : '5';

            const yt = document.createElement('div');
            yt.className = 'space-entity';
            yt.innerHTML = ytSvg;
            yt.style.zIndex = zLayer;
            document.body.appendChild(yt);

            const tg = document.createElement('div');
            tg.className = 'space-entity';
            tg.innerHTML = tgSvg;
            tg.style.zIndex = zLayer;
            document.body.appendChild(tg);

            // ورود رندوم از اطراف صفحه
            let ytX = Math.random() < 0.5 ? -200 : window.innerWidth + 200;
            let ytY = Math.random() * window.innerHeight;
            let tgX = Math.random() < 0.5 ? -200 : window.innerWidth + 200;
            let tgY = Math.random() * window.innerHeight;

            yt.style.left = ytX + 'px'; yt.style.top = ytY + 'px';
            tg.style.left = tgX + 'px'; tg.style.top = tgY + 'px';

            setTimeout(() => {{ yt.style.opacity = '1'; tg.style.opacity = '1'; }}, 50);

            let step = 0;
            const maxSteps = 3 + Math.floor(Math.random() * 2);

            function moveShips() {{
                if (step >= maxSteps) {{
                    shoot();
                    return;
                }}
                
                tgX = Math.max(100, Math.min(window.innerWidth - 100, tgX + (Math.random() - 0.5) * 800));
                tgY = Math.max(100, Math.min(window.innerHeight - 100, tgY + (Math.random() - 0.5) * 600));
                
                const tgAngle = Math.atan2(tgY - parseFloat(tg.style.top), tgX - parseFloat(tg.style.left)) * 180 / Math.PI;
                tg.style.transform = `rotate(${{tgAngle + 90}}deg)`;
                tg.style.left = tgX + 'px'; tg.style.top = tgY + 'px';

                const currentYtX = parseFloat(yt.style.left);
                const currentYtY = parseFloat(yt.style.top);
                
                ytX = tgX + (Math.random() > 0.5 ? 1 : -1) * (300 + Math.random() * 200);
                ytY = tgY + (Math.random() > 0.5 ? 1 : -1) * (300 + Math.random() * 200);
                
                const ytFlyAngle = Math.atan2(ytY - currentYtY, ytX - currentYtX) * 180 / Math.PI;
                yt.style.transform = `rotate(${{ytFlyAngle + 90}}deg)`;
                
                yt.style.left = ytX + 'px'; yt.style.top = ytY + 'px';
                
                step++;
                setTimeout(moveShips, 1200);
            }}

            function shoot() {{
                const aimAngle = Math.atan2(tgY - ytY, tgX - ytX) * 180 / Math.PI;
                yt.style.transform = `rotate(${{aimAngle + 90}}deg)`;
                
                setTimeout(() => {{
                    const willHit = Math.random() > 0.35; 
                    const doRapid = Math.random() > 0.4; 

                    function fireBullet(isSmall, isHit) {{
                        const proj = document.createElement('div');
                        proj.className = 'space-entity projectile';
                        proj.innerHTML = bulletSvg;
                        proj.style.left = ytX + 'px'; proj.style.top = ytY + 'px';
                        proj.style.zIndex = zLayer;
                        
                        if (isSmall) {{
                            proj.style.transform = `rotate(${{aimAngle + 90}}deg) scale(0.3)`;
                            proj.style.transition = 'left 0.2s linear, top 0.2s linear, opacity 0.1s';
                        }} else {{
                            proj.style.transform = `rotate(${{aimAngle + 90}}deg) scale(1)`;
                            proj.style.transition = 'left 0.4s linear, top 0.4s linear, opacity 0.2s';
                        }}
                        proj.style.opacity = '1';
                        document.body.appendChild(proj);

                        setTimeout(() => {{
                            let targetX, targetY;
                            if (isSmall || !isHit) {{
                                const spread = isSmall ? (Math.random() - 0.5) * 60 : (Math.random() > 0.5 ? 30 : -30);
                                const rad = (aimAngle + spread) * Math.PI / 180;
                                targetX = ytX + Math.cos(rad) * 2000;
                                targetY = ytY + Math.sin(rad) * 2000;
                            }} else {{
                                targetX = tgX; targetY = tgY;
                            }}
                            
                            proj.style.left = targetX + 'px';
                            proj.style.top = targetY + 'px';

                            const flightTime = isSmall ? 200 : 400;

                            if (!isSmall && !isHit) {{
                                tg.style.left = '-300px'; tg.style.top = '-300px';
                                tg.style.opacity = '0';
                            }}

                            setTimeout(() => {{
                                proj.remove();
                                if (!isSmall && isHit) {{
                                    createPixelExplosion(tgX + 40, tgY + 40, zLayer);
                                    tg.style.transform = 'scale(0)'; 
                                    tg.style.opacity = '0';
                                }}
                                if (!isSmall) {{
                                    yt.style.left = window.innerWidth + 300 + 'px';
                                    yt.style.opacity = '0';
                                    setTimeout(() => {{ yt.remove(); tg.remove(); }}, 1000);
                                }}
                            }}, flightTime);
                        }}, 20);
                    }}

                    if (doRapid) {{
                        let shots = 0;
                        const maxShots = 4 + Math.floor(Math.random() * 4);
                        const shotInterval = setInterval(() => {{
                            fireBullet(true, false); 
                            shots++;
                            if (shots >= maxShots) {{
                                clearInterval(shotInterval);
                                setTimeout(() => {{ fireBullet(false, willHit); }}, 300);
                            }}
                        }}, 120);
                    }} else {{
                        fireBullet(false, willHit);
                    }}

                }}, 400);
            }}

            setTimeout(moveShips, 200);
        }}

        function createPixelExplosion(x, y, zLayer) {{
            const colors = ['#3b82f6', '#60a5fa', '#1d4ed8', '#f1f5f9', '#94a3b8'];
            for(let i=0; i<30; i++) {{
                const p = document.createElement('div');
                p.className = 'pixel-particle';
                p.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                p.style.left = x + 'px';
                p.style.top = y + 'px';
                p.style.zIndex = zLayer;
                document.body.appendChild(p);
                
                const angle = Math.random() * Math.PI * 2;
                const distance = 40 + Math.random() * 150;
                
                setTimeout(() => {{
                    p.style.transform = `translate(${{Math.cos(angle)*distance}}px, ${{Math.sin(angle)*distance}}px) rotate(${{Math.random()*360}}deg) scale(${{Math.random() * 1.5}})`;
                    p.style.opacity = '0';
                }}, 20);
                setTimeout(() => p.remove(), 700);
            }}
        }}

        setTimeout(triggerSpaceBattle, 3000);
        setInterval(() => {{
            if (Math.random() > 0.3) triggerSpaceBattle();
        }}, 12000);

        // ----------------------------------------------------

        function submitQuickPlan(days, hours) {{
            document.getElementById('selectDays').value = days;
            document.getElementById('selectHours').value = hours;
            document.getElementById('planForm').submit();
        }}

        const holdBtn = document.getElementById('holdBtn');
        const waterFill = document.getElementById('waterFill');
        const settingsForm = document.getElementById('settingsForm');
        let holdTimer, progress = 0, isHolding = false;

        function startHold(e) {{
            if(e.cancelable) e.preventDefault();
            isHolding = true; progress = 0; waterFill.style.height = '0%';
            holdTimer = setInterval(() => {{
                progress += 2;
                waterFill.style.height = progress + '%';
                if (progress >= 100) {{
                    clearInterval(holdTimer);
                    waterFill.style.background = '#10b981';
                    document.querySelector('.water-text').innerHTML = '<i class="bi bi-check-circle-fill"></i>';
                    setTimeout(() => settingsForm.submit(), 200);
                }}
            }}, 20);
        }}

        function stopHold() {{
            isHolding = false; clearInterval(holdTimer);
            if (progress < 100) {{ progress = 0; waterFill.style.height = '0%'; }}
        }}

        holdBtn.addEventListener('mousedown', startHold);
        holdBtn.addEventListener('mouseup', stopHold);
        holdBtn.addEventListener('mouseleave', stopHold);
        holdBtn.addEventListener('touchstart', startHold, {{passive: false}});
        holdBtn.addEventListener('touchend', stopHold);

        function filterVideos(type, element) {{
            document.getElementById('currentFilterLabel').innerText = element.getAttribute(`data-${{currentLang}}`);
            document.getElementById('currentFilterLabel').setAttribute('data-en', element.getAttribute('data-en'));
            document.getElementById('currentFilterLabel').setAttribute('data-fa', element.getAttribute('data-fa'));
            
            const nowSecs = Date.now() / 1000;
            const cols = document.querySelectorAll('.video-col');
            
            cols.forEach(col => {{
                const created = parseFloat(col.getAttribute('data-created'));
                const isDeleted = col.getAttribute('data-deleted') === 'true';
                let show = false;

                if (type === 'all') {{ show = true; }} 
                else if (type === 'deleted') {{ show = isDeleted; }} 
                else if (!isDeleted) {{
                    const diff = nowSecs - created;
                    if (type === 'today' && diff <= 86400) show = true;
                    if (type === 'week' && diff <= 7 * 86400) show = true;
                    if (type === 'month' && diff <= 30 * 86400) show = true;
                }}
                col.style.display = show ? 'block' : 'none';
            }});
        }}

        const myModal = new bootstrap.Modal(document.getElementById('linkModal'));

        function showModal(token, title, direct, urldl, tg, createdAt, expiresAt, isDeleted) {{
            document.getElementById('modalTitle').innerText = title;
            document.getElementById('modalDirect').value = direct;
            
            const nowSecs = Math.floor(Date.now() / 1000);

            if (isDeleted || expiresAt < nowSecs) {{
                document.getElementById('modalDirectTime').innerText = currentLang === 'fa' ? 'حذف شده' : 'Deleted';
                document.getElementById('modalDirectTime').className = 'badge bg-danger';
            }} else {{
                const diff = expiresAt - nowSecs;
                const h = Math.floor(diff / 3600);
                const m = Math.floor((diff % 3600) / 60);
                document.getElementById('modalDirectTime').innerText = currentLang === 'fa' ? `${{h}}ساعت و ${{m}}دقیقه مانده` : `${{h}}h ${{m}}m left`;
                document.getElementById('modalDirectTime').className = 'badge bg-success';
            }}

            const urldlBox = document.getElementById('urldlBox');
            if(urldl && urldl !== 'None') {{ 
                urldlBox.style.display = 'block'; 
                document.getElementById('modalUrldl').value = urldl; 
                
                const urldlExpire = createdAt + (7 * 24 * 3600);
                if (urldlExpire < nowSecs) {{
                    document.getElementById('modalUrldlTime').innerText = currentLang === 'fa' ? 'منقضی شده' : 'Expired';
                    document.getElementById('modalUrldlTime').className = 'badge bg-danger';
                }} else {{
                    const diffU = urldlExpire - nowSecs;
                    const dU = Math.floor(diffU / 86400);
                    const hU = Math.floor((diffU % 86400) / 3600);
                    document.getElementById('modalUrldlTime').innerText = currentLang === 'fa' ? `${{dU}}روز و ${{hU}}ساعت مانده` : `${{dU}}d ${{hU}}h left`;
                    document.getElementById('modalUrldlTime').className = 'badge bg-warning text-dark';
                }}
            }} else {{ urldlBox.style.display = 'none'; }}

            const tgBox = document.getElementById('tgBox');
            if(tg && tg !== 'None') {{ 
                tgBox.style.display = 'block'; 
                document.getElementById('modalTg').value = tg; 
                document.getElementById('modalTgTime').innerText = currentLang === 'fa' ? 'دائمی' : 'Permanent';
                document.getElementById('modalTgTime').className = 'badge bg-primary';
            }} else {{ tgBox.style.display = 'none'; }}

            document.getElementById('deleteForm').action = "/admin/links/" + token + "/delete";
            myModal.show();
        }}

        function copyToClipboard(elementId) {{
            var copyText = document.getElementById(elementId);
            copyText.select();
            document.execCommand("copy");
            
            const btn = copyText.nextElementSibling;
            const originalIcon = btn.innerHTML;
            btn.innerHTML = '<i class="bi bi-check2-all text-success"></i>';
            setTimeout(() => {{ btn.innerHTML = originalIcon; }}, 1500);
        }}
    </script>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _user: str = Depends(require_admin)):
    settings = get_settings()
    
    if "expire_time" not in settings:
        settings["expire_time"] = time.time() + (30 * 24 * 3600) - 3600
        update_settings({"expire_time": settings["expire_time"]})
        
    links = store.list_links(include_expired=True)
    return _render_admin_page(settings, links, PUBLIC_BASE_URL)

@app.post("/admin/settings")
async def admin_update_settings(
    request: Request,
    enable_direct_links: bool = Form(False),
    enable_channel_delivery: bool = Form(False),
    enable_nimbaha: bool = Form(False),
    enable_urldl: bool = Form(False),
    enable_animation: bool = Form(False),
    _user: str = Depends(require_admin),
):
    if not enable_direct_links and not enable_channel_delivery:
        enable_channel_delivery = True

    new_settings = {
        "enable_direct_links": enable_direct_links,
        "enable_channel_delivery": enable_channel_delivery,
        "enable_nimbaha": enable_nimbaha,
        "enable_urldl": enable_urldl,
        "enable_animation": enable_animation,
    }

    update_settings(new_settings)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/plan/update")
async def admin_update_plan_time(
    request: Request,
    days: int = Form(0),
    hours: int = Form(0),
    _user: str = Depends(require_admin),
):
    new_expire_time = time.time() + (days * 24 * 3600) + (hours * 3600)
    update_settings({"expire_time": new_expire_time})
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/links/{token}/delete")
async def admin_delete_link(request: Request, token: str, _user: str = Depends(require_admin)):
    store.delete_link(token, delete_file=True)
    return RedirectResponse(url="/admin", status_code=303)
