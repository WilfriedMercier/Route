import dash
import dash_mantine_components   as     dmc
from   dash_iconify              import DashIconify

def hikelist_layout(language_dict : dict) -> dash.html.Div:
    r'''
    Widget containing the list of hikes.
    
    :param language_dict: dictionary containing the translation for the default language
    '''
               
    return dash.html.Div([], className='hikelist-div', id='hikelist-div')

def hikelist_element_layout(
        hike_name        : str, 
        color            : str, 
        index            : int, 
        is_selected      : bool,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> dmc.Space:
    r'''
    Widget containing a single hike shown in the sidebar.

    :param hike_name: hike name to display
    :param color: color associated to the hike
    :param index: unique identifier for this widget
    :param is_selected: whether the hike is selected at startup or not (changes its default style)
    :param language_dict: dictionary containing the translation for the default language
    :param magic_link_state: True hides the share button, False keeps it visible
    '''

    selected_style = {'backgroundColor': '#0D6EFD', 'color' : 'white', 'max-width' : '160px'} 

    button = dmc.Button(
        hike_name,
        id        = {'type' : 'hikelist-button', 'index' : index},
        className = 'hikelist-button',
        color     = 'primary',
        style     = selected_style if is_selected else {'max-width' : '160px'}
    )

    hide_button = dmc.Tooltip(
        dmc.Switch(
            offLabel = DashIconify(icon="streamline:invisible-1", width=20),
            onLabel  = DashIconify(icon="streamline:visible",     width=20),
            checked  = True,
            id        = {'type' : 'hikelist-hide-button', 'index' : index}
        ),
        label     = language_dict['hide_button']['tooltip'],
        id        = {'type' : 'hikelist-hide-button-tooltip', 'index' : index}
    )

    colorpicker = dmc.Tooltip(
        dmc.ActionIcon(
            id        = {'type' : 'hikelist-colorpicker', 'index' : index},
            className = 'colorpicker',
            color     = color,
            size      = 'lg'
        ),
        label     = language_dict['colorpicker']['tooltip'],
        id        = {'type' : 'hikelist-colorpicker-tooltip', 'index' : index}
    )

    share_button = dmc.Tooltip(
        dmc.Button(
            DashIconify(icon='material-symbols:share', width=20),
            className = 'custom-button',
            style     = {'display' : 'none' if magic_link_state else 'flex'},
            id        = {'type' : 'hikelist-share-button', 'index' : index}
        ),
        label     = language_dict['share_button']['tooltip'],
        style     = {'display' : 'none' if magic_link_state else 'flex'},
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

def hike_panel_layout(language_dict: dict) -> dmc.Drawer:
    r'''
    Sidebar widget with the list of hikes.
    
    :param language_dict: dictionary containing the translation for the default language
    '''

    hike_list = hikelist_layout(language_dict)
    upload_button = dash.dcc.Upload(
        (language_dict['upload_button']['text'],),
        className = 'custom-upload',
        id        = 'upload-hike-button',
        multiple  = True
    )

    container = dmc.Stack([hike_list, upload_button], style={'height' : '100%', 'justify-content' : 'space-between'})

    return dmc.Drawer(container, title = language_dict['title'], id = 'hike-panel')