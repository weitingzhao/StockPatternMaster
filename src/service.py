from src.engine import Engine
import src.services as service
from src.services.base_service import BaseService


class Service(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    # pull data from external data vendor
    def fetching(self) -> service.FetchingService:
        return service.FetchingService(self.Engine)

    # load data from local storage
    def loading(self) -> service.LoadingService:
        return service.LoadingService(self.Engine)
