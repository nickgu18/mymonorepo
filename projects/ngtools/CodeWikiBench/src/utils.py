import asyncio
from openai import AsyncOpenAI
import google.generativeai as genai
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
import tiktoken

from src import config


enc = tiktoken.encoding_for_model("gpt-4")

def truncate_tokens(text: str) -> str:
    """
    Count the number of tokens in a text.
    """
    tokens = enc.encode(text)

    # count tokens
    length = len(tokens)

    if length > config.MAX_TOKENS_PER_TOOL_RESPONSE:
        # truncate the text
        text = enc.decode(tokens[:config.MAX_TOKENS_PER_TOOL_RESPONSE])
        text += "\n... [truncated because it exceeds the max tokens limit, try deeper paths]"

    return text

def get_llm(model: str = None):
    """Initialize and return the specified LLM"""

    model_name = model or config.MODEL

    if model_name.startswith("gemini"):
        provider_args = {"api_key": config.API_KEY}
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            provider_args["base_url"] = config.BASE_URL

        llm_model = GoogleModel(
            model_name=model_name,
            provider=GoogleProvider(**provider_args),
            settings=GoogleModelSettings(
                temperature=0.0,
                max_tokens=36000,
                timeout=300
            )
        )
    else:
        provider_args = {"api_key": config.API_KEY}
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            provider_args["base_url"] = config.BASE_URL

        llm_model = OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(**provider_args),
            settings=OpenAIChatModelSettings(
                temperature=0.0,
                max_tokens=36000,
                timeout=300
            )
        )

    return llm_model
    
async def run_llm_natively(model: str = None, prompt: str = None, messages: list[dict] = None) -> str:
    model_name = model or config.MODEL

    if model_name.startswith("gemini"):
        genai.configure(api_key=config.API_KEY)
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            genai.configure(client_options={"api_endpoint": config.BASE_URL})

        gemini_model = genai.GenerativeModel(model_name)
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "system":
                # Gemini doesn't have a direct 'system' role in chat, treat as user for now or handle differently
                gemini_messages.append({"role": "user", "parts": [f"System instruction: {msg["content"]}"]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        response = await gemini_model.generate_content_async(gemini_messages)
        return response.candidates[0].content.parts[0].text
    else:
        client_args = {"api_key": config.API_KEY}
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            client_args["base_url"] = config.BASE_URL

        client = AsyncOpenAI(**client_args)

        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    result = asyncio.run(run_llm_natively(model="gpt-oss-120b", messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello, world!"}]))
    print(result)

# ------------------------------------------------------------
# Embeddings
# ------------------------------------------------------------

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    if config.EMBEDDING_MODEL.startswith("gemini"):
        genai.configure(api_key=config.API_KEY)
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            genai.configure(client_options={"api_endpoint": config.BASE_URL})

        response = await genai.embed_content_async(
            model=config.EMBEDDING_MODEL,
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return [embedding.values for embedding in response["embedding"]]
    else:
        client_args = {"api_key": config.API_KEY}
        if hasattr(config, "BASE_URL") and config.BASE_URL:
            client_args["base_url"] = config.BASE_URL

        client = AsyncOpenAI(**client_args)
        response = await client.embeddings.create(
            input=texts,
            model=config.EMBEDDING_MODEL,
        )

        return [embedding.embedding for embedding in response.data]



