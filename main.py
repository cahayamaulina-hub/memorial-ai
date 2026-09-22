import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import settings
from app.api.endpoints import persona, call
from app.services.persona_service import persona_service
from app.schemas.persona import PersonaCreate, MemoryItem

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API untuk Aplikasi Video Call AI Memorial (Grief Tech)"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(persona.router, prefix="/api")
app.include_router(call.router, prefix="/api")

# Mount static web and upload directories
web_dir = Path(__file__).resolve().parent.parent / "web"
web_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=web_dir), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

@app.get("/")
async def root():
    index_path = web_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Echo Memorial AI Backend is running. Frontend index.html not found yet."}

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "elevenlabs_configured": bool(settings.ELEVENLABS_API_KEY),
        "did_configured": bool(settings.DID_API_KEY)
    }

@app.on_event("startup")
async def startup_event():
    # Seed a default sample persona if empty
    existing = persona_service.list_personas()
    if not existing:
        sample_persona = persona_service.create_persona(
            PersonaCreate(
                name="Mama",
                relation="Ibu kandung",
                user_nickname="Sayang",
                tone_of_voice="Sangat lembut, keibuan, penuh kasih sayang, perhatian, menenangkan, sering menanyakan apakah sudah makan dan mengingatkan agar jangan terlalu lelah",
                core_backstory="Sosok ibu yang penuh cinta dan ketulusan, sangat suka memasak makanan hangat kesukaan keluarga di rumah, selalu menjadi tempat curhat paling nyaman dan selalu mendoakan keselamatan serta kebahagiaan anak-anaknya.",
                avatar_image_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&auto=format&fit=crop&q=80",
                greetings=[
                    "Halo sayang... Mama senang dan kangen sekali bisa melihat wajahmu lagi hari ini. Gimana kabarmu, Nak?",
                    "Sayang, lagi istirahat ya? Mama cuma mau ingatkan jangan lupa makan ya, jaga kesehatan dan jangan tidur kemalaman."
                ]
            )
        )
        # Tambahkan kenangan sampel
        persona_service.add_memory(
            sample_persona.id,
            MemoryItem(
                topic="Masakan Kesukaan",
                content="Mama selalu membuatkan sop ayam hangat dan perkedel kentang setiap kali kamu pulang dalam keadaan lelah atau sedang kurang enak badan.",
                emotional_tag="masakan"
            )
        )
        persona_service.add_memory(
            sample_persona.id,
            MemoryItem(
                topic="Nasihat Kehidupan",
                content="Mama selalu berpesan: 'Apapun yang terjadi di luar sana, jangan pernah tinggalkan doa ya sayang. Hati yang ikhlas dan sabar akan selalu membuka jalan terbaik.'",
                emotional_tag="nasihat"
            )
        )
        persona_service.add_memory(
            sample_persona.id,
            MemoryItem(
                topic="Mendengarkan Keluh Kesah",
                content="Setiap kali kamu lagi sedih atau banyak beban pikiran, Mama selalu duduk di sampingmu, mengelus rambutmu pelan-pelan sambil bilang 'semuanya akan baik-baik saja ya sayang, ada Mama di sini'.",
                emotional_tag="kenangan"
            )
        )
        print(f"[Echo] Sample persona created: {sample_persona.name} (ID: {sample_persona.id})")
