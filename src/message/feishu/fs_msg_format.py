import json
def interactive_card(card_id: str, params: dict) -> dict:
    content = json.dumps(
        {
            "type": "template",
            "data": {
                "template_id":  card_id,
                "template_variable": params,
            },
        }, ensure_ascii=False
    )
    return {
        "msg_type": "interactive",
        "content": content
    }

def plain_text(text: str) -> dict:
    content = json.dumps(
        {
            "text": text
        }, ensure_ascii=False
    )
    return {
        "msg_type": "text",
        "content": content
    }

def interactive_card_webhook(card_id: str, params: dict) -> dict:
    content = {
        "type": "template",
        "data": {
            "template_id":  card_id,
            "template_variable": params,
        },
    }
    return {
        "msg_type": "interactive",
        "card": content
    }