import dash
import dash_mantine_components   as     dmc

from .misc   import custom_colorpicker 
from ..icons import (
    IconVisible,
    IconInvisible,
    IconDelete
)

def hikelist_layout() -> dash.html.Div:
    r'''Widget containing the list of hikes.'''
               
    return dash.html.Div([], className='hikelist-div', id='hikelist-div')

def hikelist_element_layout(
        hike_name        : str, 
        color            : str,
        is_selected      : bool,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> dmc.Space:
    r'''
    Widget containing a single hike shown in the sidebar.

    :param hike_name: hike name to display and used as unique identifier
    :param color: color associated to the hike
    :param is_selected: whether the hike is selected at startup or not (changes its default style)
    :param language_dict: dictionary containing the translation for the default language
    :param magic_link_state: True hides the share button, False keeps it visible
    '''

    selected_style = {'backgroundColor': '#0D6EFD', 'color' : 'white'} 

    button = dmc.Button(
        hike_name,
        id        = {'type' : 'hikelist-button', 'index' : hike_name},
        className = 'hikelist-button',
        color     = 'primary',
        fullWidth = True,
        style     = selected_style if is_selected else {}
    )

    hide_button = dmc.Tooltip(
        dmc.Switch(
            offLabel = IconInvisible(),
            onLabel  = IconVisible(),
            checked  = True,
            id        = {'type' : 'hikelist-hide-button', 'index' : hike_name}
        ),
        label     = language_dict['hide_button']['tooltip'],
        id        = {'type' : 'hikelist-hide-button-tooltip', 'index' : hike_name}
    )

    colorpicker = dmc.Tooltip(
        custom_colorpicker(
            color, 
            {'type' : 'hikelist-colorpicker-button',  'index' : hike_name},
            {'type' : 'hikelist-colorpicker-picker',  'index' : hike_name},
            {'type' : 'hikelist-colorpicker-popover', 'index' : hike_name}
        ),
        label     = language_dict['colorpicker']['tooltip'],
        id        = {'type' : 'hikelist-colorpicker-tooltip', 'index' : hike_name}
    )

    delete_button = dmc.Button(
        IconDelete(),
        className = 'custom-button',
        style     = {'display' : 'none' if magic_link_state else 'flex'},
        id        = {'type' : 'hikelist-delete-button', 'index' : hike_name}
    )

    delete_button_tooltip = dmc.Tooltip(
        delete_button,
        label     = language_dict['delete_button']['tooltip'],
        style     = {'display' : 'none' if magic_link_state else 'flex'},
        id        = {'type' : 'hikelist-delete-button-tooltip', 'index' : hike_name}
    )

    return dmc.Space(
        [
            dmc.Group([colorpicker, button], className='hikelist-colorpicker-and-button'),
            dmc.Group([hide_button, delete_button_tooltip], className='hikelist-button-group')
        ],
        className = 'hikelist-element',
        id        = {'type' : 'hikelist-element', 'index' : hike_name}
    )

def hike_panel_layout(language_dict: dict) -> dmc.Drawer:
    r'''
    Sidebar widget with the list of hikes.
    
    :param language_dict: dictionary containing the translation for the default language
    '''

    hike_list = hikelist_layout()
    upload_button = dash.dcc.Upload(
        (language_dict['upload_button']['text'],),
        className = 'custom-upload',
        id        = 'upload-hike-button',
        multiple  = True
    )

    container = dmc.Stack([hike_list, upload_button], style={'height' : '100%', 'justify-content' : 'space-between'})

    return dmc.Drawer(container, title = language_dict['title'], id = 'hike-panel')