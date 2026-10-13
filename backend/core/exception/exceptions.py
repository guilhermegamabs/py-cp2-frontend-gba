class SensorNotFoundException(Exception):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__(f"Sensor não encontrado para a tag: {tag}")
