import json
import random
from typing import Any

import spacy
from spacy import Language
from spacy.language import PipeCallable
from spacy.training import Example
from spacy.util import minibatch
from thinc.optimizers import Optimizer
from thinc.schedules import compounding

from train_dataset import TRAIN_DATA
from core import nlp_config, logger, NLPModelTrainError


class NLPModelTrainer:
    """Класс для запуска обучения модели NLP"""

    def __init__(self):
        self._num_iter = nlp_config.num_iter

        self._nlp: Language = spacy.load(nlp_config.get_load_base_model())  # Используем обученную модель
        self._ner: PipeCallable = self.__init_ner()
        self._optimizer: None | Optimizer = None

        self._ruler: PipeCallable = self.__init_ruler()
        self._patterns: list[dict[str, str | Any]] = self.__init_patterns()

    @property
    def optimizer(self) -> Optimizer:
        """
        Инициируем/получаем Optimizer для обновления весов модели при обучении.

        @rtype: Optimizer
        @return:
        """
        if not self._optimizer and nlp_config.is_resume_training:
            self._optimizer = self._nlp.resume_training()

        elif not self._optimizer and not nlp_config.is_resume_training:
            self._optimizer = self._nlp.initialize()

        return self._optimizer

    def __init_ner(self) -> PipeCallable:
        """
        Добавляем к модели компонент 'ner'.

        @rtype ner: PipeCallable
        @return ner:
        """
        if nlp_config.ner_pipe not in self._nlp.pipe_names:
            ner = self._nlp.add_pipe(nlp_config.ner_pipe)

        else:
            ner = self._nlp.get_pipe(nlp_config.ner_pipe)

        for label in nlp_config.ner_labels:
            ner.add_label(label)

        return ner

    def __init_ruler(self) -> PipeCallable:
        """
        Инициируем работу с паттернами дл поиска сущностей в тексте.

        @rtype ruler: PipeCallable
        @return ruler:
        """
        if nlp_config.rule_pipe not in self._nlp.pipe_names:
            ruler: PipeCallable = self._nlp.add_pipe(nlp_config.rule_pipe, before=nlp_config.ner_pipe)

        else:
            ruler: PipeCallable = self._nlp.get_pipe(nlp_config.rule_pipe)

        return ruler

    def __init_patterns(self) -> list[dict[str, str | Any]]:
        """
        Добавление паттернов обучения модели.

        @rtype patterns: list[dict[str, str | Any]]
        @return patterns:
        """
        try:
            with open(nlp_config.pattern_path, "r") as fp:
                patterns = json.load(fp)

        except FileNotFoundError:
            raise NLPModelTrainError(message=f"File with patterns not found (file path: {nlp_config.pattern_path})")

        new_patterns = list()
        for pattern in patterns:
            if not self.__pattern_exists(pattern_to_check=pattern):
                new_patterns.append(pattern)

        if new_patterns:
            self._ruler.add_patterns(new_patterns)

        return patterns

    def __pattern_exists(self, pattern_to_check: dict[str, str | Any]) -> bool:
        """
        Проверка - паттерн уже добавлен в ner-модель.

        @type pattern_to_check: dict[str, str | Any]
        @param pattern_to_check:
        @rtype patterns: list[dict[str, str | Any]]
        @return patterns:
        """
        return any(
            pattern["label"] == pattern_to_check["label"] and
            pattern["pattern"] == pattern_to_check["pattern"]
            for pattern in self._ruler.patterns
        )

    async def run(self) -> None:
        """
        Запуск обучения модели.

        @rtype: None
        @return:
        """
        size_ = compounding(2.0, 8.0, 1.001)

        for n_iter in range(self._num_iter):
            losses = dict()
            random.shuffle(TRAIN_DATA)

            for batch in minibatch(TRAIN_DATA, size=size_):
                examples = list()

                for text, annotations_ in batch:
                    doc_ = self._nlp.make_doc(text)
                    examples.append(Example.from_dict(doc_, annotations_))

                self._nlp.update(examples, drop=nlp_config.model_drop, losses=losses, sgd=self.optimizer)
            logger.info(f"Num iteration {n_iter + 1} — losses: {losses}")

        self._nlp.to_disk(nlp_config.output_dir_path)
        logger.info(f"NLP model was train, train data: {len(TRAIN_DATA)}")
