from   abc  import ABC, abstractmethod
import dash

class BaseWidget(ABC):

    def __init__(self, app: dash.Dash) -> None:

        self._app    = app
        self._layout = None

        return
    
    @property
    def app(self) -> dash.Dash: return self._app

    @property
    def layout(self): return self._layout

    @abstractmethod
    def _init_layout(self): return