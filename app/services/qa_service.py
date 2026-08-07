import logging
import re

from groq import AsyncGroq

from app.config import config

logger = logging.getLogger(__name__)

_client: AsyncGroq | None = None

# Cap the outbound Telegram message so we stay well under the 4096-char limit.
MAX_ANSWER_CHARS = 3600
MAX_SOURCES = 5

SYSTEM_PROMPT = (
    "You are a helpful assistant answering user questions inside a Telegram chat. "
    "When the question involves current events, prices, dates, versions, people's "
    "current roles, or anything that could change over time, USE the web search "
    "tool to ground your answer in up-to-date information. Answer concisely and "
    "clearly. The user may write in English, Khmer (ភាសាខ្មែរ), or a mix — reply in "
    "the same language as the question. If sources disagree or the answer isn't "
    "clear, say so instead of guessing."
)


_URL_PATTERN = re.compile(r"https?://[^\s\])>\"'}]+")


def _extract_sources(message) -> list[str]:
    """Pull source URLs out of a Groq compound-model response.

    Compound models return `executed_tools` on the message; each tool call has
    an `output` string containing the search results. We regex URLs out of it.
    Falls back to any URLs cited in the answer body itself.
    """
    urls: list[str] = []
    executed = getattr(message, "executed_tools", None) or []
    for tool in executed:
        # `tool` may be a pydantic model, dict, or namespace — handle all shapes.
        output = None
        if hasattr(tool, "output"):
            output = getattr(tool, "output", None)
        elif isinstance(tool, dict):
            output = tool.get("output")
        if not output:
            continue
        if not isinstance(output, str):
            output = str(output)
        for match in _URL_PATTERN.findall(output):
            clean = match.rstrip(".,);]")
            if clean not in urls:
                urls.append(clean)
            if len(urls) >= MAX_SOURCES:
                return urls
    return urls


def _get_client() -> AsyncGroq | None:
    global _client
    if _client is not None:
        return _client
    if not config.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — Q&A feature disabled.")
        return None
    _client = AsyncGroq(api_key=config.GROQ_API_KEY)
    return _client


async def ask_gemini(question: str) -> str:
    """Send a free-form user question to Groq and return the answer text.

    Function name is kept as `ask_gemini` for backwards compatibility with
    existing imports in `handlers/messages.py`.
    """
    question = (question or "").strip()
    if not question:
        return "❓ Please include your question in the reply."

    client = _get_client()
    if client is None:
        return "⚠️ AI answers are not available — the server is missing a GROQ_API_KEY."

    try:
        response = await client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.4,
            max_tokens=1024,
        )
        message = response.choices[0].message
        answer = (message.content or "").strip()
        if not answer:
            return "🤔 I couldn't produce an answer for that. Try rephrasing?"

        sources = _extract_sources(message)
        if len(answer) > MAX_ANSWER_CHARS:
            answer = answer[:MAX_ANSWER_CHARS].rstrip() + "…"
        if sources:
            answer = f"{answer}\n\n🔗 Sources:\n" + "\n".join(f"• {url}" for url in sources)
        return answer
    except Exception as e:
        err_str = str(e)
        status = getattr(e, "status_code", None)
        if status == 429 or "429" in err_str or "rate_limit" in err_str.lower():
            logger.warning(f"Groq rate limit hit: {e}")
            return "⚠️ AI is rate-limited right now. Please wait a moment and try again."
        if status in (401, 403) or "invalid_api_key" in err_str.lower() or "unauthorized" in err_str.lower():
            logger.error(
                "Groq rejected the credentials. Check GROQ_API_KEY in .env — get a key at "
                "https://console.groq.com/keys"
            )
            return "⚠️ The bot's Groq API key is invalid. Please contact the admin to fix it."
        logger.error(f"Groq Q&A failed: {e}")
        return "⚠️ Sorry, something went wrong while asking the AI. Please try again."
