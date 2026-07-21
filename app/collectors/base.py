from abc import ABC, abstractmethod

from app.models.threat import Threat


class BaseCollector(ABC):
    """Каждый источник данных реализует этот интерфейс.
    Это то, что делает архитектуру расширяемой: чтобы добавить новый
    источник, не нужно трогать ничего, кроме одного нового файла."""

    source_name: str = "unknown"

    @abstractmethod
    def fetch(self) -> list[Threat]:
        """Возвращает список нормализованных Threat-объектов."""
        raise NotImplementedError
