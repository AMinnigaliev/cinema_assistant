from infi.clickhouse_orm import Model, fields
from infi.clickhouse_orm.engines import MergeTree


class VoiceAssistantRequestModel(Model):
    """Модель данных по входящему запросу."""

    __table__ = 'voice_assistant_request'

    user_id = fields.StringField()
    request_id = fields.StringField()
    status = fields.StringField(default="in_progress")
    transcription = fields.StringField()
    tts_file_path = fields.StringField()
    stt_file_path = fields.StringField()
    found_entities = fields.StringField()
    timestamp = fields.DateTimeField()

    engine = MergeTree("timestamp", ("user_id", "request_id"))


class NERTrainingData(Model):
    """Модель данных для обучения NER-модели на основе входящих запросов."""

    __table__ = 'ner_training_data'

    request_id = fields.StringField()
    status = fields.StringField(default="not_approved")
    training_data = fields.StringField()
    timestamp = fields.DateTimeField()

    engine = MergeTree("timestamp", ("request_id", ))
