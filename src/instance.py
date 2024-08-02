import src


class Instance:

    def __init__(self):
        # Step 1. Init Config
        self._config = src.Config()
        self._logger: src.Logger = self._config.logger
        self._tools: src.Tools = src.Tools(self._config.logger)
        # tier 2. Base on Config init Engine
        self._engine = src.Engine(self._config)
        # Step 3. Base on Engine init Service
        self._service = src.Service(self._engine)
        # Step 4. Base on Service init Analyze
        self._analyse = src.Analyse(self._service)
        # Step 5. Base on Analyze init Chart
        self._chart = src.Chart(self._analyse)
