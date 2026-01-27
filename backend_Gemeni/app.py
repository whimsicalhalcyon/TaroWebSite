from contextlib import asynccontextmanager
from functools import lru_cache
import json
from pathlib import Path
import re
from fastapi import FastAPI, HTTPException
from fastapi.params import Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from pydantic import BaseModel
import uvicorn

from layout import TarotModel

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
api_model = os.getenv("GEMENI_MODEL", "gemini-2.5-flash-lite")
BASE_DIR = Path(__file__).resolve().parent

if not api_key or api_key.strip() == "":
    print("WARNING: GEMINI_API_KEY is not set. API will not work.")
    print("Set it using: docker exec -it tarot-api env GEMINI_API_KEY=your_key")
    client = None
else:
    client = genai.Client(api_key=api_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading card data...")
    load_card_data()
    print("Card data loaded successfully")
    yield
    print("Shutting down...")

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


app = FastAPI(lifespan=lifespan)

app.mount("/tarotdeck", StaticFiles(directory=BASE_DIR / "tarotdeck"), name="tarotdeck")
@app.get("/tarot", response_model=TarotResponse)
async def get_tarot_reading(
    option: str = Query(..., pattern="^(linear|balance|advice)$"),
    query: str = Query(..., min_length=10, max_length=500)
):
    try:
        model = TarotModel(option, query, data=load_card_data())

        cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', query))
        language = "ru" if cyrillic > 0 else "en"
        async def event_stream():
            # Отправляем начальные данные
            initial_data = {
                "option": option,
                "query": query,
                "cards": model.cards,
                "language": language
            }
            yield f"data: {json.dumps(initial_data, ensure_ascii=False)}\n\n"
            
            # Стримим ответ от Gemini
            response_stream = client.models.generate_content_stream(
                model=api_model,
                contents=model.query,
                config=types.GenerateContentConfig(
                    system_instruction=model.prompt
                )
            )
            
            for chunk in response_stream:
                if chunk.text:
                    chunk_data = {"answer_chunk": chunk.text}
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            
            # Сигнал завершения
            yield "data: {\"done\": true}\n\n"
        
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Card data file not found")
    except TimeoutError:
        raise HTTPException(status_code=504, detail="LLM generation timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")



if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")