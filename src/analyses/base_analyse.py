from src.service import Service
from src.services.base_service import BaseService


class BaseAnalyse(BaseService):

    def __init__(self, service: Service):
        super().__init__(service.Engine)
        self.Service = service
