from openai import  OpenAI

from config.ai import MODEL_CONFIG, ModelProvider

SYSTEM_PROMPT = "You are a helpful assistant."

def create_client(provider: ModelProvider) -> OpenAI:
    """Create OpenAI client for specified provider"""
    config = MODEL_CONFIG.get(provider)
    if not config:
        raise ValueError(f"Unsupported provider: {provider}")

    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )

def ai_chat(prompt, system=SYSTEM_PROMPT, provider: ModelProvider = ModelProvider.ALIYUN) -> str:
    client = create_client(provider)
    config = MODEL_CONFIG[provider]
    response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
    return response.choices[0].message.content

def ai_chat_json(prompt, response_format, system=SYSTEM_PROMPT, provider: ModelProvider = ModelProvider.ALIYUN):
    client = create_client(provider)
    config = MODEL_CONFIG[provider]
    response = client.beta.chat.completions.parse(
            model=config['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format
        )
    return response.choices[0].message.content


if __name__ == "__main__":

    res = ai_chat("你好", provider=ModelProvider.OLLAMA_FAST)
    print(res)