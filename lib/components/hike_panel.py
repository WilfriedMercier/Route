import dash
import dash_mantine_components   as     dmc
import dash_bootstrap_components as     dbc
import plotly.graph_objects      as     go
from   dash_iconify              import DashIconify

from   .base                     import BaseWidget
    
class HikeList(BaseWidget):
    r'''
    Widget containing the list of hikes.
    
    :param app: main application used for callback handling
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    '''

    def __init__(self, app: dash.Dash, hikes: dict[str, dict]) -> None:

        super().__init__(app)

        self._init_layout(hikes)
        self._register_callbacks()

        return
    
    @property
    def buttons(self): return self._buttons
    
    def _init_layout(self, hikes: dict[str, dict] | None) -> None:
        r'''
        Initialize the hike list widget's layout.
        
        :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
        '''

        self._buttons: list[HikeListElement] = []

        if hikes is not None: 
                
            for pos, (hike_name, properties) in enumerate(hikes.items()):
                self._buttons.append(
                    HikeListElement(self._app, hike_name, properties['color'], pos, is_selected=pos==0)
                )

        self._layout = dash.html.Div([button.layout for button in self._buttons], className='hikelist-div')

        return

    def _register_callbacks(self):
        r'''Callback used whenever a hike is clicked in the hike list.'''

        @self.app.callback(
            dash.Output({'type' : 'hikelist-button', 'index' : dash.ALL}, 'style'),
            dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
            prevent_initial_call = True
        )
        def button_callback(*args) -> list[dict[str, str] | dash.NoUpdate]:

            ctx = dash.callback_context

            if not ctx.triggered:
                return [dash.no_update] * len(self.buttons)

            # Extract the ID of the clicked button
            clicked_id = int(
                ctx.triggered[0]['prop_id']
                .split('.')[0]
                .split('index', maxsplit=1)[1]
                .split(',',     maxsplit=1)[0]
                .split('}',     maxsplit=1)[0]
                .strip(',:{}"\'')
            )
    
            # Update style
            return [
                {'backgroundColor': 'var(--custom-theme-color)', 'color' : 'white'}
                if button.id == clicked_id else {} 
                for button in self.buttons
            ]

class HikeListElement(BaseWidget):
    r'''
    Widget containing a single hike shown in the sidebar.

    :param app: main application used for callback handling
    :param hike_name: hike name to display
    :param color: color associated to the hike
    :param idd: unique identifier for this widget
    :param is_selected: whether the hike is selected at startup or not (changes its default style)
    '''

    def __init__(self, app: dash.Dash, hike_name: str, color: str, idd: int, is_selected: bool = False) -> None:
        
        super().__init__(app)

        self._id             = idd
        self._hike_name      = hike_name
        self._selected_style = {'backgroundColor': '#0D6EFD', 'color' : 'white'} 

        self._init_layout(is_selected, hike_name, color)
        self._register_callbacks()

        return
    
    @property
    def id(self) -> int: return self._id
    
    @property
    def selected_style(self) -> dict: return self._selected_style

    @property
    def hike_name(self) -> str: return self._hike_name
    
    def _init_layout(self, is_selected: bool, hike_name: str, color: str) -> None:
        r'''
        Initialize the layout for this element.

        :param is_selected: whether this element is selected at startup
        :param hike_name: name of the hike
        :param color: color shown in the colorpicker widget
        '''

        button = dmc.Button(
            hike_name,
            id        = {'type' : 'hikelist-button', 'index' : self.id},
            className = 'hikelist-button',
            color     = 'primary',
            style     = self.selected_style if is_selected else {}
        )

        hide_button = dmc.Tooltip(
            dmc.Switch(
                offLabel = DashIconify(icon="streamline:invisible-1", width=20),
                onLabel  = DashIconify(icon="streamline:visible",     width=20),
                checked  = True,
                id        = {'type' : 'hikelist-hide-button', 'index' : self.id}
            ),
            label     = self.app.lang['hike_panel']['hide_button']['tooltip'],
            openDelay = 1000,
            id        = {'type' : 'hikelist-hide-button-tooltip', 'index' : self.id}
        )

        colorpicker = dmc.Tooltip(
            dbc.Input(
                id        = {'type' : 'hikelist-colorpicker', 'index' : self.id},
                className = 'hikelist-colorpicker',
                value     = color,
                type      = 'color' , # type: ignore
            ),
            label     = self.app.lang['hike_panel']['colorpicker']['tooltip'],
            openDelay = 1000,
            id        = {'type' : 'hikelist-colorpicker-tooltip', 'index' : self.id}
        )

        self._layout = dbc.Row(
            [
                dbc.Col(dash.html.Div(
                    [colorpicker, button], 
                    style = {'display' : 'flex', 'alignItems' : 'center', 'gap' : '5px'}), 
                    width = 'auto'
                ),
                dbc.Col(hide_button, width='auto')
            ],
            className = 'hikelist-element',
            id        = f'hikelist-element-{self.id}'
        )

        return
    
    def _register_callbacks(self) -> None:

        @self.app.callback([
                #dash.Output('elevation-plot', 'figure', allow_duplicate = True),
                dash.Output('map', 'figure', allow_duplicate = True)
            ],
            dash.Input({'type' : 'hikelist-button', 'index' : self.id}, 'n_clicks'),
            dash.State('map', 'figure'),
            prevent_initial_call = True
        )
        def hike_button_callback(_, map_dict: dict) -> tuple[go.Figure]:
            '''
            Callback called whenever the given hike is clicked.
            
            :param map_dict: current state of the map plot 
            '''

            # Get distances and elevations for the given hike
            info = self.app.hikes_data[self.hike_name]

            #info['distances'], info['elevations'], info['color']

            map_figure = go.Figure(map_dict)

            map_figure.update_layout(
                mapbox= {
                    'center' : {'lat' : info['center'][0], 'lon' : info['center'][1]},
                    'zoom'   : info['zoom']
                }
            )

            return map_figure,

        @self.app.callback(
            dash.Output('map', 'figure', allow_duplicate=True),
            dash.Input({'type' : 'hikelist-colorpicker', 'index' : self.id}, 'value'),
            dash.State('map', 'figure'),
            prevent_initial_call=True
        )
        def colorpicker_callback(color: str, map_dict: dict) -> go.Figure:

            map_figure = go.Figure(map_dict)
            map_figure.update_traces(
                line     = {'color' : color},
                selector = self.id + 1
            )

            return map_figure
        
        @self.app.callback(
            [
                dash.Output({'type' : 'hikelist-button',      'index' : self.id}, 'disabled'),
                dash.Output({'type' : 'hikelist-colorpicker', 'index' : self.id}, 'disabled'),
                dash.Output('map', 'figure', allow_duplicate=True)
            ],
            dash.Input({'type' : 'hikelist-hide-button', 'index' : self.id}, 'checked'),
            dash.State('map', 'figure'),
            dash.State({'type' : 'hikelist-colorpicker', 'index' : self.id}, 'value'),
            prevent_initial_call = True
        )
        def hide_button_callback(
            checked: bool, map_dict: dict, color: str
        ) -> tuple[bool, bool, go.Figure]:
            r'''
            Callback used when the hide button is toggled.

            :param checked: whether the hide button is checked
            :param map_dict: current layout for the map
            :param color: current color of the associated colorpicker
            '''

            map_figure = go.Figure(map_dict)
            map_figure.update_traces(
                line     = {
                    'color' : 'rgba(0, 0, 0, 0)' if not checked else color
                },
                selector = self.id + 1
            )

            return (not checked, not checked, map_figure)
            
        
        return

        return

class HikePanel(BaseWidget):
    r'''
    Class responsible for building the sidebar with the list of hikes.
    
    :param app: main application used for callback handling
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    '''

    def __init__(self, app: dash.Dash, hikes: dict[str, dict]) -> None:

        super().__init__(app)
        self._init_layout(hikes)

        return
    
    @property
    def hike_list(self) -> HikeList: return self._hike_list

    def _init_layout(self, hikes: dict[str, dict]) -> None:
        r'''
        Initialize the sidebar with a list of hikes.
        
        :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
        '''

        self._hike_list = HikeList(self.app, hikes)

        self._layout = dmc.Drawer(
            self.hike_list.layout,
            title   = self.app.lang['hike_panel']['title'],
            id      = 'hike-panel'
        )

        return