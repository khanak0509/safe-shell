from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash'
)

