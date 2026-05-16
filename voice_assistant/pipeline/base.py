from abc import ABC, abstractmethod
from typing import Any, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BasePipelineStage(ABC):
    """Base class for all pipeline stages"""

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass

    def __call__(self, input_data: Any) -> Any:
        return self.process(input_data)
