import os
from pathlib import Path

import aiohttp

from core import config, SearchEngineError, logger
from voice_mixins import STTMixin, TTSMixin
from models import IncomingVoiceData, OutgoingVoiceData
from assistant_model_worker import AssistantModelWorkerMixin


class VoiceSearchEngine(STTMixin, TTSMixin, AssistantModelWorkerMixin):
    """Класс по поиску запрашиваемой информации (фильмов) из входящего аудиофайла."""

    def __init__(self, incoming_d: dict[str, str]) -> None:
        self._incoming_voice_d = IncomingVoiceData(**incoming_d)

    @property
    def get_not_found_voice_path(self) -> str:
        """
        Получение аудиофайла "По вашему запросу ничего не найдено."

        @rtype: str
        @return:
        """
        if not os.path.exists(config.not_found_voice_path):
            self._gen_not_found_tts()

        return config.not_found_voice_path

    async def run(self) -> dict[str, str]:
        out_voice_path = self.get_not_found_voice_path
        in_voice_stt = self.gen_stt(voice_data=self._incoming_voice_d)

        out_text = config.tts_not_found_response
        if prediction := self.named_entity_recognition(text=in_voice_stt):
            if found_entities := await self._find_entities_by_prediction(prediction=prediction):
                out_voice_path, out_text = self.gen_tts(
                    found_entities=found_entities,
                    user_id=self._incoming_voice_d.user_id,
                )

        outgoing_voice_d = self._gen_outgoing_voice_data(out_voice_path=out_voice_path, out_text=out_text)
        self.del_incoming_voice_file(file_path=self._incoming_voice_d.incoming_voice_path)

        return outgoing_voice_d

    async def _find_entities_by_prediction(self, prediction: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Поиск запрашиваемых из входящего аудиофайла сущностей (фильмов) в movies_service.

        @type prediction: dict[str, list[str]]
        @param prediction: Извлеченные из входящего аудиофайла запросы на поиск сущностей.
        @rtype found_entities: list[dict[str, str | Any]]
        @return found_entities:
        """
        found_entities = dict()

        if requested_movies := prediction.get(config.movie_label):
            movies_for_search = list()  # TODO: требуется правка модели (убрать слово 'фильм')
            for movie in requested_movies:
                if movie.startswith("фильм "):
                    movie = movie.removeprefix("фильм ")

                movies_for_search.append(movie)

            if movies_by_titles := await self._get_movies_by_titles(movies=movies_for_search):
                found_entities[config.movie_label] = movies_by_titles

        return found_entities

    async def _get_movies_by_titles(self, movies: list[str]) -> list[str]:
        """
        Поиск фильмов из входящего аудиофайла в movies_service.

        @type movies: list[str]
        @param movies: Наименования запрашиваемых фильмов.
        @rtype: list[str]
        @return:
        """
        query_data = {"search": movies[0], "page_size": 3, "page_number": 1}  # TODO: movies[0]

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{config.get_movies_service_url()}/{config.movies_service_uri['search_films_by_title']}"
                headers = {
                    "Accept": "application/json",
                    "x-request-id": self._incoming_voice_d.request_id,
                }
                response = await session.get(url, params=query_data, headers=headers)

                if response.status != 200:
                    logger.error(f"[!] Error get data(url={url}, query_data={query_data}): code = {response.status}")
                    return []

                films = await response.json()
                return [film["title"] for film in films] if films else []

        except Exception as ex:
            raise SearchEngineError(
                message=f"Error get data(url={url}, query_data={query_data}): {ex}",
                code="movies-service-error",
            )

    def _gen_outgoing_voice_data(self,out_voice_path: str, out_text: str) -> dict[str, str]:
        outgoing_voice_data = OutgoingVoiceData(
            request_id=self._incoming_voice_d.request_id,
            user_id=self._incoming_voice_d.user_id,
            output_voice_path=out_voice_path,
            out_text=out_text,
        )

        return outgoing_voice_data.dict()

    @staticmethod
    def del_incoming_voice_file(file_path: str) -> None:
        path = Path(file_path)

        if path.exists():
            path.unlink()
