import os
import google.generativeai as genai

API_KEY = os.environ.get("GENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set the GENAI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

response = model.generate_content(
    "Review this code: print('hello')"
)

print(response.text)