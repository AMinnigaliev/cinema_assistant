import os.path
from datetime import datetime

import speech_recognition as sr
from gtts import gTTS

from core import config, logger
from models import IncomingVoiceData


class STTMixin:
    """Mixin - speech to text операция."""

    @staticmethod
    def gen_stt(voice_data: IncomingVoiceData) -> str | None:
        recognizer = sr.Recognizer()

        with sr.AudioFile(voice_data.incoming_voice_path) as source:
            audio_data = recognizer.record(source)

            try:
                text: str = recognizer.recognize_google(audio_data, language=config.language_recognize)
                logger.debug(f"[STT] text was gen, file_path={voice_data.incoming_voice_path}")

                return text

            except sr.UnknownValueError as ex:
                logger.error(f"[STT] speech recognition failed: {ex}")

            except sr.RequestError as ex:
                logger.error(f"[STT] speech recognition server error: {ex}")


class TTSMixin:
    """Mixin - text to speech операция."""

    @staticmethod
    def gen_tts(found_entities: dict[str, list[str]], user_id: str) -> tuple[str, str]:
        datetime_now = datetime.now().replace(microsecond=0).isoformat()
        output_file_name = f"out_{user_id}_{datetime_now}.mp3"
        output_file_path = os.path.join(config.outgoing_file_path, output_file_name)

        found_movies = ', '.join(found_entities.get(config.movie_label, []))
        text = config.tts_response_template.format(found_movies=found_movies)

        try:
            tts = gTTS(text=text, lang=config.language_tts)
            tts.save(output_file_path)

        except Exception as ex:
            logger.error(f"[TTS] not correct error: {ex}")

        return output_file_path, text

    @staticmethod
    def _gen_not_found_tts() -> None:
        text = config.tts_not_found_response

        try:
            tts = gTTS(text=text, lang=config.language_tts)
            tts.save(config.not_found_voice_path)

        except Exception as ex:
            logger.error(f"[TTS] not correct error: {ex}")
