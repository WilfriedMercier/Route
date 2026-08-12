import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..types                  import HikeInfo
from   ..lang                   import LANGUAGE
from   ..components.magic_links import magic_link_container_item
from   ..icons import (
    IconCheck,
    IconEdit,
    IconChevronDown,
    IconChevronUp
)

def register_magic_link_panel_callbacks(app: dash.Dash) -> None:

    @app.callback(
        dash.Output({'type' : 'magic-link-collapse-title-edit-button', 'index' : dash.MATCH}, 'children'),
        dash.Output({'type' : 'magic-link-collapse-title', 'index' : dash.MATCH}, 'readOnly'),
        dash.Output({'type' : 'magic-link-collapse-title', 'index' : dash.MATCH}, 'styles'),

        dash.Input({'type' : 'magic-link-collapse-title-edit-button', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State({'type' : 'magic-link-collapse-title', 'index' : dash.MATCH}, 'readOnly'),
        prevent_initial_call = True
    )
    def title_edit_button_click(_, title_readonly: bool) -> tuple[DashIconify, bool, dict]:
        r'''
        Callback used when on of the edit title buttons in the magic link panel is clicked.

        :param title_readonly: whether the title is in readonly state or not

        :returns: a tuple with
            - the new icon for the edit title button
            - True if the title was not readonly, False otherwise
            - a styles dictionary for the title edit widget
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        if title_readonly:
            icon   = IconCheck()
            styles = {
                'input' : {
                    'color'           : 'darkOrange',
                    'borderColor'     : 'darkOrange', 
                    'backgroundColor' : 'var(--input-bg)',
                    'cursor'          : 'text'
                }
            }
        else:
            icon   = IconEdit()
            styles = {'input' : {'backgroundColor': 'transparent', 'cursor' : 'default'}}

        return icon, not title_readonly, styles

    @app.callback(
        dash.Output({'type' : 'magic-link-collapse', 'index' : dash.MATCH}, 'opened'),
        dash.Output({'type' : 'magic-link-collapse-button', 'index' : dash.MATCH}, 'children'),

        dash.Input({'type' : 'magic-link-collapse-button', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State({'type' : 'magic-link-collapse', 'index' : dash.MATCH}, 'opened'),
        prevent_initial_call = True
    )
    def magic_link_collapse_button_click(_, opened: bool) -> tuple[bool, DashIconify]:
        r'''
        Callback used when one of the collapse buttons is clicked in the magic link panel.

        :param opened: whether the collapsible area is opened or not

        :returns: a tuple with
            - True if the collapsible area was closed, False otherwise
            - the new icon for the collapse button
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        if opened : icon = IconChevronDown()
        else      : icon = IconChevronUp()

        return not opened, icon

    @app.callback(
        dash.Output('magic-link-container', 'children'),
        dash.Input('add-magic-link',        'n_clicks'),
        dash.State('magic-link-container',  'children'),
        dash.State('language', 'data'),
        dash.State('hikes-info', 'data')
    )
    def add_magic_link_click(
            _, 
            children   : list[dmc.Stack], 
            language   : LANGUAGE, 
            hikes_info : dict[str, HikeInfo]
        ) -> dash.Patch:

        if _ is None: raise dash.exceptions.PreventUpdate

        translation = app.language_handler[language]
        name        = f'Magic link #{len(children)}'

        new_child = magic_link_container_item(
            name, 
            name, 
            translation['magic_link_panel']['item'],
            list(hikes_info.keys())
        )

        patch = dash.Patch()
        patch.prepend(new_child)

        return patch

    @app.callback(
        dash.Output('appshell', 'navbar', allow_duplicate=True),
        dash.Input({'type' : 'magic-link-multiselect', 'index' : dash.MATCH}, 'value'),
        prevent_initial_call=True
    )
    def magic_link_multiselect_change(value: list):
        raise dash.exceptions.PreventUpdate

    return