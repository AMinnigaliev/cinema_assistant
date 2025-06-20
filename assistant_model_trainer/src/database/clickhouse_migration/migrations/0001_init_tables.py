from models.clickhouse_models import VoiceAssistantRequestModel, NERTrainingData


def migrate(session):
    models = [VoiceAssistantRequestModel, NERTrainingData]

    for model in models:
        if not session.does_table_exist(model):
            session.create_table(model)
