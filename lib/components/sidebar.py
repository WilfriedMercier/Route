import dash
import dash_bootstrap_components as     dbc
from   ..lang                    import LanguageEnum, LanguageHandler

class Sidebar:
    r'''
    Class responsible for building the sidebar with the list of hikes.
    
    :param app: main application used for callback handling
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    :param translations: dictionary containing the translations of the UI elements of the sidebar
    :param default_language: default language to be displayed
    '''

    def __init__(
            self, 
            app              : dash.Dash, 
            hikes            : dict[str, dict], 
            translations     : dict, 
            default_language : LanguageEnum = LanguageEnum.ENGLISH
        ) -> None:

        self._app = app

        # Component handling the language translation for this widget
        self._language_handler = LanguageHandler(translations, default_language)

        self._build_layout(hikes)

        self._register_callbacks()

        return
    
    def _build_layout(self, hikes: dict[str, dict]) -> None:
        r'''
        Build the sidebar with a list of hikes.
        
        :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
        '''

        self.toggle_button = dbc.Button(
            id        = 'sidebar-toggle',
            children  = dash.html.I(className="bi bi-arrows-angle-contract"), 
            className = 'mb-1',
            color     = 'secondary'
        )

        self.title = dash.html.P(
            self._language_handler['title'], 
            className = 'text-muted mb-4',
            id        = 'sidebar-title'
        )

        self.hike_list = HikeList(self._app, hikes)

        self.main = dbc.Collapse(
            dash.html.Div([self.title, self.hike_list.layout], className="sidebar-main-inner"),
            id      = 'sidebar-collapsible-content',
            is_open = True
        )

        self.layout = dash.html.Div([self.toggle_button, self.main], className='sidebar-container')

        return
    
    def update_layout_language(self, lang: LanguageEnum) -> None:
        r'''
        Update the language of the elements in the layout.

        :param: new language to apply
        '''

        self._language_handler.language = lang
        self.title.children             = self._language_handler['title']

        return
    
    def _register_callbacks(self):

        @self._app.callback(
            [
                dash.Output('sidebar-collapsible-content', 'is_open'),
                dash.Output('sidebar-toggle', 'children')
            ],
            [dash.Input('sidebar-toggle', 'n_clicks')],
            [dash.State('sidebar-collapsible-content', 'is_open')]
        )
        def toggle_sidebar_callback(
            n       : int | None, 
            is_open : bool
        ) -> tuple[bool, dash.html.I] | tuple[dash.NoUpdate, dash.NoUpdate]:

            if n and is_open:
                return False, dash.html.I(className=u"bi bi-arrows-angle-expand")
            elif n and not is_open:
                return True, dash.html.I(className=u"bi bi-arrows-angle-contract")

            return dash.no_update, dash.no_update

        return
    
class HikeList:
    r'''
    Widget containing the list of hikes.
    
    :param app: main application used for callback handling
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    '''

    def __init__(self, app: dash.Dash, hikes: dict[str, dict]) -> None:

        self._app = app

        self._build_layout(hikes)
        self._register_callbacks()

        return
    
    def _build_layout(self, hikes: dict[str, dict] | None) -> None:
        r'''
        Build the hike list widget's layout.
        
        :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
        '''

        if hikes is None: return

        self.buttons: list[HikeListElement] = []

        for pos, (hike_name, properties) in enumerate(hikes.items()):
            self.buttons.append(
                HikeListElement(self._app, hike_name, properties['color'], pos, is_selected=pos==0)
            )

        self.layout = dash.html.Div([button.layout for button in self.buttons], id='hikelist')

        return

    def _register_callbacks(self):
        r'''Callback used whenever a hike is clicked in the hike list.'''

        @self._app.callback(
            dash.Output({'type' : 'hikelist-button', 'index' : dash.ALL}, 'style'),
            dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
            prevent_initial_call = True
        )
        def button_callback(*args):

            ctx = dash.callback_context

            if not ctx.triggered:
                return [dash.no_update] * len(self.buttons)

            # Extract the ID of the clicked button
            clicked_id = int(
                ctx.triggered[0]['prop_id']
                .split('.')[0]
                .split('index', maxsplit=1)[1]
                .split(',', maxsplit=1)[0]
                .split('}', maxsplit=1)[0]
                .strip(',:{}"\'')
            )
    
            # Update style
            return [
                {'backgroundColor': '#0D6EFD', 'color' : 'white'} 
                if button._id == clicked_id else {} 
                for button in self.buttons
            ]
        
        return

class HikeListElement:
    r'''
    Widget containing a single hike shown in the sidebar.

    :param app: main application used for callback handling
    :param hike_name: hike name to display
    :param color: color associated to the hike
    :param idd: unique identifier for this widget
    :param is_selected: whether the hike is selected at startup or not (changes its default style)
    '''

    def __init__(self, app: dash.Dash, hike_name: str, color: str, idd: int, is_selected: bool = False) -> None:
        
        self._app        = app

        self.hike_name   = hike_name
        self.color       = color
        self._id         = idd

        self.hidden      = False
        self.highlighted = False

        self._build_layout(is_selected)
        self._register_callbacks()

        return
    
    @property
    def id(self) -> int: return self._id

    @property
    def app(self) -> dash.Dash: return self._app
    
    @property
    def icon_shown(self) -> dash.html.I:
        return dash.html.I(className="bi bi-eye-fill")
    
    @property
    def icon_hidden(self) -> dash.html.I:
        return dash.html.I(className="bi bi-eye-slash")
    
    @property
    def selected_style(self) -> dict:
        return {'backgroundColor': '#0D6EFD', 'color' : 'white'} 
    
    def _build_layout(self, is_selected: bool) -> None:

        self.button = dbc.Button(
            self.hike_name,
            id        = {'type' : 'hikelist-button', 'index' : self._id},
            className = 'hikelist-button',
            outline   = True,
            color     = 'primary',
            style     = self.selected_style if is_selected else {}
        )

        self.hide_button = dash.dcc.Button(
            self.icon_shown,
            className = 'hikelist-hide-button',
            id        = f'hikelist-hide-button-{self._id}'
        )

        self.colorpicker = dbc.Input(
            id        = f'hikelist-colorpicker-{self._id}',
            className = 'hikelist-colorpicker',
            value     = self.color,
            type      = 'color' , # type: ignore
        )

        self.layout = dbc.Row(
            [
                dbc.Col(dash.html.Div([
                    self.colorpicker,
                    self.button
                ], style={'display' : 'flex', 'alignItems' : 'center', 'gap' : '5px'}), width='auto'),
                dbc.Col(self.hide_button, width='auto')
            ],
            className = 'hikelist-element',
            id        = f'hikelist-element-{self._id}'
        )

        return
    
    def _register_callbacks(self) -> None:

        @self.app.callback([
                dash.Output(f'hikelist-hide-button-{self._id}', 'children'),
                dash.Output(f'hikelist-colorpicker-{self._id}', 'disabled'),
                dash.Output({'type' : 'hikelist-button', 'index' : self._id}, 'disabled')
            ],
            dash.Input(f'hikelist-hide-button-{self._id}', 'n_clicks'),
            prevent_initial_call=True
        )
        def hide_button_callback(*args) -> tuple[dash.html.I, bool, bool]:
            r'''Callback used whenever the hide button is triggered for this widget.'''

            if self.hidden: 
                icon = self.icon_shown
            else:           
                icon = self.icon_hidden

            self.hidden = not self.hidden

            return icon, self.hidden, self.hidden
        
        @self.app.callback(
            dash.Output('elevation-plot', 'figure', allow_duplicate = True,),
            dash.Input({'type' : 'hikelist-button', 'index' : self._id}, 'n_clicks'),
            prevent_initial_call = True
        )
        def hike_button_callback(*args) -> None:

            # Get distances and elevations for the given hike
            info = self.app.ui.hikes_data[self.hike_name]

            map_widget = self.app.ui.map_page

            map_widget.update_layout_data(info['distances'], info['elevations'], info['color'])

            return map_widget.elevation_plot.fig