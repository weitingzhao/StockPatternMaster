import src


class Instance:

    def __init__(self):
        # Step 1. Init Config
        self.Config = src.Config()
        self.Logger: src.Logger = self.Config.logger
        self.Tools: src.Tools = src.Tools(self.Config.logger)
        # tier 2. Base on Config init Engine
        self.Engine = src.Engine(self.Config)
        # Step 3. Base on Engine init Service
        self.Service = src.Service(self.Engine)
        # Step 4. Base on Service init Analyze
        self.Analyse = src.Analyse(self.Service)
        # Step 5. Base on Analyze init Chart
        self.Chart = src.Chart(self.Analyse)
