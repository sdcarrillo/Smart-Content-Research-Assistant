from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os 
load_dotenv()

MODEL_CONFIG = {
    "cheap": os.getenv("AZURE_OPENAI_CHEAP_DEPLOYMENT"),
    "standard": os.getenv("AZURE_OPENAI_STANDARD_DEPLOYMENT"),
    "premium": os.getenv("AZURE_OPENAI_PREMIUM_DEPLOYMENT")
}

def get_llm(tier:str):
    model_name = MODEL_CONFIG[tier]

    if not model_name:
        raise ValueError(f"No hay deployment para tier {tier}")

    if not (os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY")):
        raise RuntimeError("Faltan variables de entorno de Azure OpenAI")
    
    return init_chat_model(
        model=model_name,
        model_provider="azure_openai",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        temperature=0.0
    )

def llm_invoke(tier: str, system_prompt: str, user_prompt: str) -> str:
    llm = get_llm(tier)
    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_prompt.strip()},
    ]
    res = llm.invoke(messages)
    
    # print(f"[models] invocando {tier.upper()} -> {model_name}")
    return getattr(res, "content", str(res))
