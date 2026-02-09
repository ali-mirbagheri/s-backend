from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from kavenegar import KavenegarAPI, APIException, HTTPException as KHTTP
from dotenv import load_dotenv
import os

# ---------- ENV ----------
load_dotenv()
KAVENEGAR_API_KEY = os.getenv("KAVENEGAR_API_KEY")

if not KAVENEGAR_API_KEY:
    raise RuntimeError("❌ KAVENEGAR_API_KEY is not set")

# ---------- APP ----------
app = FastAPI(title="Romantic SMS API 💌")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = KavenegarAPI(KAVENEGAR_API_KEY)

# ---------- MODELS ----------
class SMSRequest(BaseModel):
    phone: str = Field(..., example="09123456789")
    message: str = Field(..., min_length=1, max_length=500)

# ---------- HELPERS ----------
def send_sms_task(phone: str, message: str):
    try:
        params = {
            "receptor": phone,
            "message": message,
            "sender": 2000660110
            # ⚠️ sender رو عمداً نذاشتیم (برای جلوگیری از 400)
        }
        result = api.sms_send(params)
        print("✅ SMS SENT:", result)

    except APIException as e:
        print("❌ KAVENEGAR API ERROR:", e)

    except KHTTP as e:
        print("❌ KAVENEGAR HTTP ERROR:", e)


# ---------- ROUTES ----------
@app.post("/send-sms")
def send_sms(data: SMSRequest, bg: BackgroundTasks):
    # ✅ Validation
    if not data.phone.startswith("09") or len(data.phone) != 11:
        raise HTTPException(status_code=400, detail="شماره موبایل نامعتبره")

    # ✅ Async SMS (UI معطل نمی‌مونه)
    bg.add_task(send_sms_task, data.phone, data.message)

    return {
        "ok": True,
        "message": "درخواست ارسال پیامک ثبت شد 💌"
    }
