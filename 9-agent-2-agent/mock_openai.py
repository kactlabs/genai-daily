from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/openai")
async def mock_openai(request: Request):
    data = await request.json()
    prompt = data.get("messages")[0]["content"].lower()
    
    if "palindrome" in prompt:
        answer = "Palindrome"
    elif "reverse" in prompt:
        answer = "ReverseText"
    elif "@" in prompt or "email" in prompt:
        answer = "EmailValidator"
    else:
        answer = "EmailValidator"

    return JSONResponse(content={
        "choices": [{
            "message": {
                "content": answer
            }
        }]
    })

# Run with: uvicorn mock_openai:app --port 5000
