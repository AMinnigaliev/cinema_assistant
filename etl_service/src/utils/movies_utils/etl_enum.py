import enum


class RuleTypes(enum.Enum):
    SELECTION_RULE = "selection_rule"
    NORMALIZE_RULE = "normalize_rule"
    ENRICH_RULE = "enrich_rule"


class OperationTypes(enum.Enum):
    MODIFIED = "modified"
    INSERT = "insert"


class PersonRoles(enum.Enum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITER = "writer"
