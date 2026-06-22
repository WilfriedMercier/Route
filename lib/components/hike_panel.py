import dash
import dash_mantine_components   as     dmc
import dash_bootstrap_components as     dbc
from   dash_iconify              import DashIconify

def hikelist_layout(hikes: dict[str, dict], language_dict : dict) -> dash.html.Div:
    r'''
    Widget containing the list of hikes.
    
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    '''

    buttons = []

    if hikes is not None: 
            
        for pos, (hike_name, properties) in enumerate(hikes.items()):
            buttons.append(
                hikelist_element_layout(hike_name, properties['color'], pos, pos==0, language_dict)
            )
               
    return dash.html.Div(buttons, className='hikelist-div')

def hikelist_element_layout(
        hike_name     : str, 
        color         : str, 
        index         : int, 
        is_selected   : bool,
        language_dict : dict
    ) -> dmc.Space:
    r'''
    Widget containing a single hike shown in the sidebar.

    :param hike_name: hike name to display
    :param color: color associated to the hike
    :param index: unique identifier for this widget
    :param is_selected: whether the hike is selected at startup or not (changes its default style)
    :param language_dict: dictionary containing the translation for the default language
    '''

    selected_style = {'backgroundColor': '#0D6EFD', 'color' : 'white'} 

    button = dmc.Button(
        hike_name,
        id        = {'type' : 'hikelist-button', 'index' : index},
        className = 'hikelist-button',
        color     = 'primary',
        style     = selected_style if is_selected else {}
    )

    hide_button = dmc.Tooltip(
        dmc.Switch(
            offLabel = DashIconify(icon="streamline:invisible-1", width=20),
            onLabel  = DashIconify(icon="streamline:visible",     width=20),
            checked  = True,
            id        = {'type' : 'hikelist-hide-button', 'index' : index}
        ),
        label     = language_dict['hide_button']['tooltip'],
        openDelay = 1000,
        id        = {'type' : 'hikelist-hide-button-tooltip', 'index' : index}
    )

    colorpicker = dmc.Tooltip(
        dbc.Input(
            id        = {'type' : 'hikelist-colorpicker', 'index' : index},
            className = 'hikelist-colorpicker',
            value     = color,
            type      = 'color' , # type: ignore
        ),
        label     = language_dict['colorpicker']['tooltip'],
        openDelay = 1000,
        id        = {'type' : 'hikelist-colorpicker-tooltip', 'index' : index}
    )

    share_button = dmc.Tooltip(
        dmc.Button(
            DashIconify(icon='material-symbols:share', width=20),
            className = 'custom-button',
            id        = {'type' : 'hikelist-share-button', 'index' : index}
        ),
        label     = language_dict['share_button']['tooltip'],
        openDelay = 1000,
        id        = {'type' : 'hikelist-share-button-tooltip', 'index' : index}
    )

    return dmc.Space(
        [
            dmc.Group([colorpicker, button]),
            dmc.Group([share_button, hide_button])
        ],
        className = 'hikelist-element',
        id        = f'hikelist-element-{index}'
    )

def hike_panel_layout(hikes: dict[str, dict], language_dict: dict) -> dmc.Drawer:
    r'''
    Sidebar widget with the list of hikes.
    
    :param hikes: dictionary where the keys are hike names and the values are dictionaries with associated values (e.g. color)
    :param language_dict: dictionary containing the translation for the default language
    '''

    hike_list = hikelist_layout(hikes, language_dict)
    upload_button = dash.dcc.Upload(
        ['Drag and drop or click to upload a hike'], 
        className = 'custom-upload',
        multiple  = True
    )

    container = dmc.Stack([hike_list, upload_button], style={'height' : '100%', 'justify-content' : 'space-between'})

    return dmc.Drawer(container, title = language_dict['title'], id = 'hike-panel')