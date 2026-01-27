import asyncio
from functools import lru_cache
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from ctransformers import AutoModelForCausalLM
from pydantic import BaseModel
from contextlib import asynccontextmanager
from layout import TarotModel
from translator import detect_language, translate_query_to_english, translate_response_to_russian
from dotenv import load_dotenv
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading card data...")
    load_card_data()
    print("Card data loaded successfully")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "tinyllama-tarot-q4_k_m.gguf"
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)

try:
    llm_model = AutoModelForCausalLM.from_pretrained(
        os.getenv("BASE_DIR", str(BASE_DIR)),
        model_file=os.getenv("MODEL_FILE", str(MODEL_PATH.name)),
        model_type=os.getenv("MODEL_TYPE", "llama"),
        context_length=int(os.getenv("CONTEXT_LENGTH", "3072")),
        threads=int(os.getenv("THREADS", "6")),
        gpu_layers=int(os.getenv("GPU_LAYERS", "0")),
        batch_size=int(os.getenv("BATCH_SIZE", "512")),
    )
    print("LLM model loaded successfully")
except Exception as e:
    raise RuntimeError(f"Failed to load LLM model: {e}")

@lru_cache(maxsize=1)
def load_card_data():
    card_path = BASE_DIR / "card_data.json"
    with open(card_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
class TarotResponse(BaseModel):
    option: str
    query: str
    cards: list
    answer: str
    language: str

@app.get("/tarot", response_model=TarotResponse)
async def get_tarot_reading(
    option: str = Query(..., pattern="^(linear|balance|advice)$"),
    query: str = Query(..., min_length=1, max_length=500)
):
    try:
        lang = detect_language(query)
        if lang != "en":
            query = translate_query_to_english(query)
            
        model = TarotModel(option, query, data=load_card_data())

        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            lambda: llm_model(
                model.prompt,
                max_new_tokens=int(os.getenv(f"{option.upper()}_MAX_NEW_TOKENS", "800")),
                temperature=float(os.getenv(f"{option.upper()}_TEMPERATURE", "0.7")),
                top_k=int(os.getenv(f"{option.upper()}_TOP_K", "25")),
                top_p=float(os.getenv(f"{option.upper()}_TOP_P", "0.85")),
                repetition_penalty=float(os.getenv(f"{option.upper()}_REPETITION_PENALTY", "1.15")),
                stop = [
                    "</s>",
                    "[INST]",
                    "Question:",
                    "Cards:",
                    "\n\n\n\n",
                    "QUESTION:",
                ],
                stream=False,
            ).strip()
        )

        if lang != "en":
            answer = translate_response_to_russian(answer)

        return TarotResponse(
            option=option,
            query=query,
            cards=model.cards,
            answer=answer,
            language=lang
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Card data file not found")
    except TimeoutError:
        raise HTTPException(status_code=504, detail="LLM generation timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")