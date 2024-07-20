import uvicorn
from src.api import app as api_app
from multiprocessing import Process

class API_Handler():
    """
    Class to handle the subprocess where the localhost API runs.
    """
    def __init__(self):
        """
        Initialize API.
        """
        self.api_process = False

    def api_worker(self):
        """
        Worker that runs the localhost API.
        """
        uvicorn.run(api_app)

    def kill_api(self):
        """
        Terminates the localhost API process.
        """
        if self.api_process:
            self.api_process.terminate()
            self.api_process = False

    def start_api(self):
        """
        Starts the localhost API process.
        """
        if not self.api_process:
            self.api_process = Process(target=self.api_worker, daemon=True)
            self.api_process.start()
