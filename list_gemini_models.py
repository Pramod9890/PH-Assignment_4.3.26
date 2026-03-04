from dotenv import load_dotenv
load_dotenv("Environment.env")  # This loads variables from your file into the OS environment
import os
import google.generativeai as genai

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))  # Should print your key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
print(list(genai.list_models()))