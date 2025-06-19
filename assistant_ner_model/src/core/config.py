import os

from pydantic import BaseSettings, Field


class NLPConfig(BaseSettings):
    """NER (Named Entity Recognizer) конфигурации."""

    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(default="assistant_ner_model")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    num_iter: int = Field(default=30, alias="NLP_NUM_ITER")
    output_dir_path: str = Field(default=os.path.join(base_dir, "movie_ner_model"))

    model_name: str = Field(default="ru_core_news_sm")
    model_drop: float = Field(default=0.2)
    ner_pipe: str = Field(default="ner")
    rule_pipe: str = Field(default="entity_ruler")

    pattern_path: str = Field(default=os.path.join(base_dir, "train_patterns.json"))
    ner_labels: list[str] = Field(default=["MOVIE"])
    is_resume_training: bool = Field(default=True, alias="NLP_IS_RESUME_TRAINING")

    ner_task_trigger: str = Field(default="interval", alias="NER_TASK_TRIGGER")
    ner_task_interval_days: int = Field(default=1, alias="NER_TASK_INTERVAL_DAYS")

    def get_load_base_model(self, train_type: bool = True) -> str:
        """
        Определение основной модели для обучения:
        - Выбирается обученная модель 'ru_core_news_sm' и на ее основе происходит дообучение модели.
        - Выбирается ранее обученная модель 'movie_ner_model' и проходит дообучение (additional).

        @type train_type: bool
        @param train_type: Флаг - обучение модели с нуля(на основе 'ru_core_news_sm') или дообучение существующей.
        @rtype: str
        @return:
        """
        if train_type:
            if os.path.isdir(self.output_dir_path):
                return self.output_dir_path

        return self.model_name


nlp_config = NLPConfig()
