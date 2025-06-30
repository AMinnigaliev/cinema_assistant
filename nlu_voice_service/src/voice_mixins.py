import os
import asyncio
from datetime import datetime

import speech_recognition as sr
from gtts import gTTS

from core import config, logger
from models import IncomingVoiceData


class STTMixin:
    """Mixin - speech to text операция."""

    @staticmethod
    async def gen_stt(voice_data: IncomingVoiceData) -> str | None:
        def recognize():
            recognizer = sr.Recognizer()

            with sr.AudioFile(voice_data.incoming_voice_path) as source:
                audio_data = recognizer.record(source)

                try:
                    text: str = recognizer.recognize_google(
                        audio_data,
                        language=config.language_recognize,
                    )
                    debug_msg = (
                        f"[STT] text was gen, "
                        f"file_path={voice_data.incoming_voice_path}"
                    )
                    logger.debug(debug_msg)

                    return text

                except sr.UnknownValueError as ex:
                    logger.error(f"[STT] speech recognition failed: {ex}")

                except sr.RequestError as ex:
                    logger.error(
                        f"[STT] speech recognition server error: {ex}"
                    )

        return await asyncio.to_thread(recognize)


class TTSMixin:
    """Mixin - text to speech операция."""

    @staticmethod
    async def gen_tts(
        found_entities: dict[str, list[str]],
        user_id: str,
    ) -> tuple[str, str]:
        def generate():
            datetime_now = datetime.now().replace(microsecond=0).isoformat()
            output_file_name = f"out_{user_id}_{datetime_now}.mp3"
            output_file_path = os.path.join(
                config.outgoing_file_path,
                output_file_name,
            )

            found_movies = ', '.join(
                found_entities.get(config.movie_label, [])
            )
            text = config.tts_response_template.format(
                found_movies=found_movies,
            )

            try:
                tts = gTTS(text=text, lang=config.language_tts)
                tts.save(output_file_path)

            except Exception as ex:
                logger.error(f"[TTS] not correct error: {ex}")

            return output_file_path, text

        return await asyncio.to_thread(generate)

    @staticmethod
    async def _gen_not_found_tts() -> None:
        def generate():
            text = config.tts_not_found_response

            try:
                tts = gTTS(text=text, lang=config.language_tts)
                tts.save(config.not_found_voice_path)

            except Exception as ex:
                logger.error(f"[TTS] not correct error: {ex}")

        return await asyncio.to_thread(generate)
