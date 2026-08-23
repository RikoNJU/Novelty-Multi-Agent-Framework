from backend.env import (
    ChatMessage,
    ImageContentPart,
    ModelCallOptions,
    ModelProfile,
    OpenAICompatibleChatClient,
)


def make_client() -> OpenAICompatibleChatClient:
    profile = ModelProfile(
        alias="ocr",
        model="deepseek-ai/DeepSeek-OCR",
        base_url="https://example.test/v1",
        api_key="test-key",
    )
    return OpenAICompatibleChatClient(profile)


def test_text_only_content_stays_string():
    payload = make_client()._build_payload(
        [ChatMessage(role="user", content="你好")],
        ModelCallOptions(),
    )

    assert payload["messages"][0]["content"] == "你好"


def test_multimodal_content_serializes_vision_format():
    payload = make_client()._build_payload(
        [
            ChatMessage(
                role="user",
                content=[
                    ImageContentPart(image_url="data:image/png;base64,AAAA"),
                    "请识别图片中的文字",
                ],
            )
        ],
        ModelCallOptions(max_tokens=512),
    )

    content = payload["messages"][0]["content"]
    assert content[0] == {
        "type": "image_url",
        "image_url": {"url": "data:image/png;base64,AAAA", "detail": "high"},
    }
    assert content[1] == {"type": "text", "text": "请识别图片中的文字"}


def test_multimodal_content_supports_custom_detail():
    payload = make_client()._build_payload(
        [
            ChatMessage(
                role="user",
                content=[ImageContentPart(image_url="data:image/png;base64,BB", detail="low")],
            )
        ],
        ModelCallOptions(),
    )

    assert payload["messages"][0]["content"][0]["image_url"]["detail"] == "low"
