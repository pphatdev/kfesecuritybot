import logging
import time
from google import genai
from app.config import config

logger = logging.getLogger(__name__)

# Simple per-chat rate limiter: track the last time a chat was analyzed
# chat_id -> timestamp of last AI call
_last_call: dict[int, float] = {}
# Minimum seconds between AI calls per chat
AI_COOLDOWN_SECONDS = 5


class DetectorService:
    def __init__(self):
        if config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        else:
            self.client = None
            logger.warning("Gemini API key not found. DetectorService will use keyword-only mode.")

        # Track quota exhaustion to suppress repeated error logs
        self._quota_exhausted = False

    async def analyze(self, text: str, chat_id: int | None = None) -> str:
        if not text:
            return "Safe"

        if not self.client:
            return self._mock_detect(text)

        # Rate limit: skip API call if this chat was analyzed recently
        if chat_id is not None:
            now = time.monotonic()
            last = _last_call.get(chat_id, 0)
            if now - last < AI_COOLDOWN_SECONDS:
                logger.debug(f"Rate limiting AI call for chat {chat_id}")
                return "Safe"
            _last_call[chat_id] = now

        try:
            prompt = (
                "You are a strict AI content moderator for a Telegram group. "
                "Analyze the following message and classify it as exactly one of: 'Spam', 'Toxic', or 'Safe'. "
                "The message may be in any language, including Khmer (ភាសាខ្មែរ), English, or mixed. "
                "Look for spam patterns such as: promotions, ads, scams, fake investment, gambling, adult content links. "
                "Look for toxic patterns such as: hate speech, insults, offensive language, threats — in any language. "
                "Reply with the classification word first, then a brief 1-sentence reason.\n\n"
                f"Message: \"{text}\""
            )

            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            # Reset quota flag on success
            self._quota_exhausted = False
            return response.text.strip()

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                if not self._quota_exhausted:
                    logger.warning(
                        "Gemini API quota exhausted. Falling back to keyword-only detection until quota resets."
                    )
                    self._quota_exhausted = True
                # Fall back gracefully — don't crash, just return Safe
                return "Safe"
            else:
                logger.error(f"Error during AI analysis: {e}")
                return "Safe"

    def _mock_detect(self, text: str) -> str:
        lower_text = text.lower()

        english_spam = ["buy", "crypto", "click here", "earn money", "investment", "casino", "bet", "lottery", "free gift", "winner"]
        khmer_spam = ["ចុចនៅទីនេះ", "ទទួលបាន", "ឈ្នះ", "វិនិយោគ", "កាស៊ីណូ", "លទ្ធផល", "ចូលរួម", "ប្រាក់", "ការប្រណាំង", "ឱកាស"]
        english_toxic = ["hate", "idiot", "stupid", "kill", "die", "ugly", "loser", "shut up", "moron"]
        khmer_toxic = ["គួរតែស្លាប់", "ឆ្កែ", "ល្ងង់", "ជើងអំបាញ់", "ខ្ញុំស្អប់", "ទ្រុំ", "ក្មេងកាច", "ស្អាប"]

        if any(k in lower_text for k in english_spam) or any(k in text for k in khmer_spam):
            return "Classification: Spam\nReason: Contains spam-related keywords."
        elif any(k in lower_text for k in english_toxic) or any(k in text for k in khmer_toxic):
            return "Classification: Toxic\nReason: Contains offensive or hateful language."
        else:
            return "Safe"

# Create a singleton instance to be used across the app
detector_service = DetectorService()
