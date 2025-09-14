# import google.generativeai as genai
# import time

# # 🔑 Direct Gemini API Key (replace with your actual key)
# GEMINI_API_KEY = "AIzaSyDJVDY-eb0EEd1bUxMRKD4Tbv1x8pEZ-3c"

# def configure_gemini():
#     """Configure the Gemini API with the provided key"""
#     try:
#         genai.configure(api_key=GEMINI_API_KEY)
#         return True
#     except Exception as e:
#         print(f"Error configuring Gemini: {e}")
#         return False

# def generate_response(prompt, chat_history=None):
#     """Generate a response using Google's Gemini model"""
#     try:
#         # Configure Gemini
#         if not configure_gemini():
#             return "Error: Gemini API not configured properly. Please check your API key."
        
#         # Set up the model
#         generation_config = {
#             "temperature": 0.7,
#             "top_p": 0.8,
#             "top_k": 40,
#             "max_output_tokens": 1024,
#         }

#         safety_settings = [
#             {
#                 "category": "HARM_CATEGORY_HARASSMENT",
#                 "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#             },
#             {
#                 "category": "HARM_CATEGORY_HATE_SPEECH",
#                 "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#             },
#             {
#                 "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#                 "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#             },
#             {
#                 "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#                 "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#             },
#         ]

#         # Initialize the model
#         model = genai.GenerativeModel(
#             model_name="gemini-2.5-flash",
#             generation_config=generation_config,
#             safety_settings=safety_settings
#         )
        
#         # Prepare conversation history
#         conversation = []
#         if chat_history:
#             for message in chat_history:
#                 role = "user" if message.role == "user" else "model"
#                 conversation.append({
#                     "role": role,
#                     "parts": [message.content]
#                 })
        
#         # Add the new prompt
#         conversation.append({"role": "user", "parts": [prompt]})
        
#         # Generate response
#         response = model.generate_content(conversation)
#         return response.text
        
#     except Exception as e:
#         error_msg = f"Sorry, I encountered an error: {str(e)}"
#         print(error_msg)
#         return error_msg

# # Alternative simpler function if you're having issues with the chat history
# def generate_simple_response(prompt):
#     """Generate a simple response without chat history"""
#     try:
#         if not configure_gemini():
#             return "Error: Gemini API not configured properly."
        
#         # Initialize the model
#         model = genai.GenerativeModel("gemini-pro")
        
#         # Generate response
#         response = model.generate_content(prompt)
#         return response.text
        
#     except Exception as e:
#         return f"Sorry, I encountered an error: {str(e)}"
import time
import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def configure_gemini():
    """Configure the Gemini API with the provided key"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        raise

def generate_response(prompt, chat_history=None):
    """Generate a response using Google's Gemini model"""
    try:
        # Check if API key is set
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set")
            return "Sorry, the AI service is not configured properly. Please check the API settings."
        
        configure_gemini()

        # ✅ Use minimal tokens to save cost/quota
        generation_config = {
            "temperature": 0.5,         # lower randomness
            "top_p": 0.7,               # tighter probability sampling
            "top_k": 20,                # fewer candidate tokens
            "max_output_tokens": 1024,   # shorter replies → fewer tokens
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",   # ⚡ faster & cheaper
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # ✅ Add delay BEFORE sending request (rate limiting / throttling)
        time.sleep(2)

        # Prepare conversation history
        conversation = []
        if chat_history:
            for message in chat_history:
                role = "user" if message.role == "user" else "model"
                conversation.append({"role": role, "parts": [message.content]})
        
        conversation.append({"role": "user", "parts": [prompt]})

        # Generate response
        response = model.generate_content(conversation)

        # ✅ Safe parsing
        if response.candidates:
            for cand in response.candidates:
                if cand.content and cand.content.parts:
                    return cand.content.parts[0].text.strip()

        finish_reason = (
            response.candidates[0].finish_reason if response.candidates else "unknown"
        )
        logger.warning(f"Gemini API returned empty response (finish_reason={finish_reason})")
        return "I'm sorry, I couldn't generate a response this time."

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Sorry, I encountered an error: {str(e)}. Please try again later."
