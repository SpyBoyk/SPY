import google.generativeai as genai

# paste the correct Gemini API key here
genai.configure(api_key="AIzaSyDJVDY-eb0EEd1bUxMRKD4Tbv1x8pEZ-3c")

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Hello! Can you summarize Gemini API in one line?")
print(response.text)
