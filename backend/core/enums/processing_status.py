from enum import Enum


class ProcessingStatus(str, Enum):
    IN_PROGRESS = "EM_PROCESSAMENTO"
    DONE = "CONCLUIDA"
    FAILED = "FALHA"
