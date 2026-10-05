class SensorNotFoundException(Exception):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__(f"Sensor não encontrado para a tag: {tag}")


class SensorOfflineException(Exception):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__(f"Sensor {tag} está desligado e não publica leitura no momento.")
