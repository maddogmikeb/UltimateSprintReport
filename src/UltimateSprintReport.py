from atlassian import Jira
from tqdm.auto import tqdm
import os 
import importlib

class UltimateSprintReport(object):
      
      def __init__(self,	username: str, password: str, jira_scheme_url: str):
         if (jira_scheme_url is None) or (username is None) or (password is None):
            raise ValueError("Jira scheme URL, username and password are required")
         self.jira = Jira(url=jira_scheme_url, username=username, password=password, cloud=True)

         self.PluginFolder = "./plugins"
         self.MainModule = "__init__"

      # Imported methods
      from .utils import calculate_predictability_score_stars 

      # Some more small functions
      def printHi(self):
        self.progress_bar = tqdm(total=100, desc="Loading Sprint Details", leave=True)

      def getPlugins(self):
         plugins = []
         possible_plugins = os.listdir(self.PluginFolder)
         for i in possible_plugins:
            location = os.path.join(self.PluginFolder, i)
            if not os.path.isdir(location) or not self.MainModule + ".py" in os.listdir(location):
                  continue
            info = importlib.find_module(self.MainModule, [location])
            plugins.append({"name": i, "info": info})
         return plugins

      def loadPlugin(self, plugin):         
         return importlib.load_module(self.MainModule, *plugin["info"])