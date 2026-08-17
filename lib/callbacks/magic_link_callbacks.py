import dash
import random
from   dash_iconify import DashIconify
from   flask        import session

from ..errors                   import NoHikeForMagicLink
from ..misc                     import COLOR_PALETTE
from ..database                 import Magic_links_table, Magic_links_props_table, Hikes_table
from ..components.notifications import share_hike_notification, hike_title_update_notification
from ..lang                     import LANGUAGE
from ..components.magic_links   import magic_link_container_item, magic_link_hike_element_row
from ..types                    import HikeInfo, DashComplexID, Notification
from ..icons import (
    IconCheck,
    IconEdit,
    IconChevronDown,
    IconChevronUp
)

def register_magic_link_panel_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to the magic link panel.
    
    :param app: Dash application
    '''

    @app.callback(
        dash.Output({'type' : 'magic-link-collapse-title-edit-button', 'index' : dash.ALL}, 'children'),
        dash.Output({'type' : 'magic-link-collapse-title', 'index' : dash.ALL}, 'readOnly'),
        dash.Output({'type' : 'magic-link-collapse-title', 'index' : dash.ALL}, 'styles'),
        dash.Output({'type' : 'magic-link-collapse-title-edit-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),
        dash.Output("notification-container", 'sendNotifications', allow_duplicate = True),

        dash.Input({'type' : 'magic-link-collapse-title-edit-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State({'type' : 'magic-link-collapse-title', 'index' : dash.ALL}, 'id'),
        dash.State({'type' : 'magic-link-collapse-title', 'index' : dash.ALL}, 'readOnly'),
        dash.State({'type' : 'magic-link-collapse-title', 'index' : dash.ALL}, 'value'),
        dash.State('language', 'data'),
        prevent_initial_call = True
    )
    def title_edit_button_click(
            _, 
            all_ids         : list[DashComplexID], 
            titles_readonly : list[bool], 
            titles          : list[str],
            language        : LANGUAGE
        ) -> tuple[
            list[DashIconify | dash.NoUpdate], 
            list[bool | dash.NoUpdate], 
            list[dict | dash.NoUpdate], 
            list[str  | dash.NoUpdate],
            list[Notification] | dash.NoUpdate
        ]:
        r'''
        Callback used when on of the edit title buttons in the magic link panel is clicked.

        :param all_ids: ids of all the titles
        :param titles_readonly: whether each title is in readonly state or not
        :param titles: all the titles
        :param language: language of the UI

        :returns: a tuple with lists containing dash.no_update everywhere except for the element corresponding to the triggered ID with
            - the new icon for the edit title button
            - True if the title was not readonly, False otherwise
            - a styles dictionary for the title edit widget,
            - a list containing an updated tooltip for the edit title button
            - a list containing a notification to show or a no update
        '''

        triggered_id = dash.callback_context.triggered_id

        if all(i is None for i in _) or triggered_id is None: raise dash.exceptions.PreventUpdate

        # Find the position of the element with the right index
        pos   = [idd['index'] == triggered_id['index'] for idd in all_ids].index(True)

        if _[pos] is None: raise dash.exceptions.PreventUpdate

        ll = len(all_ids)

        # Do not update elements that do not match the triggered id
        icons: list[dash.NoUpdate | DashIconify]    = [dash.no_update] * ll
        readonly_states: list[dash.NoUpdate | bool] = [dash.no_update] * ll
        styles: list[dash.NoUpdate | dict]          = [dash.no_update] * ll
        tooltips: list[dash.NoUpdate | str]         = [dash.no_update] * ll

        # Case when the title must become editable
        if title_readonly := titles_readonly[pos]:

            tooltips[pos]        = app.language_handler[language]['magic_link_panel']['item']['edit_title_button']['validate']['tooltip']
            notification         = dash.no_update
            readonly_states[pos] = not title_readonly
            icons[pos]           = IconCheck()
            styles[pos]          = {
                'input' : {
                    'color'           : 'darkOrange',
                    'borderColor'     : 'darkOrange', 
                    'backgroundColor' : 'var(--input-bg)',
                    'cursor'          : 'text'
                }
            }

        # Case when the title is validated
        else:

            tooltips[pos]        = app.language_handler[language]['magic_link_panel']['item']['edit_title_button']['edit']['tooltip']
            readonly_states[pos] = not title_readonly
            icons[pos]           = IconEdit()
            styles[pos]          = {'input' : {'backgroundColor': 'transparent', 'cursor' : 'default'}}
            notification         = [
                hike_title_update_notification(
                    app.language_handler[language]['notifications']
            )]

            # Update the name in the database
            Magic_links_table.update_magic_link_name(
                triggered_id['index'],
                titles[pos]
            )

        return icons, readonly_states, styles, tooltips, notification

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
        dash.State('language', 'data'),
        dash.State('hikes-info', 'data'),
        running=[
            (dash.Output('add-magic-link', "disabled"), True, False),
            (dash.Output('add-magic-link-tooltip', "disabled"), True, False),
            (dash.Output('magic-link-overlay', "visible"), True, False)
        ]
    )
    def add_magic_link_click(
            _,
            language   : LANGUAGE, 
            hikes_info : dict[str, HikeInfo]
        ) -> dash.Patch:
        r'''
        Callback used when the add magic link button is clicked.

        :param language: current language of the UI
        :param hikes_info: information about the hikes
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        translation = app.language_handler[language]

        # Create a new magic link in the database with a random name
        n          = random.randint(0, 1_000_000)
        name       = f'Magic link #{n}'

        magic_link = Magic_links_table.insert_row(name, session['user_id'])

        new_child = magic_link_container_item(
            magic_link, 
            name,
            translation['magic_link_panel']['item'],
            [],
            [],
            list(hikes_info.keys())
        )

        patch = dash.Patch()
        patch.prepend(new_child)
        
        return patch

    @app.callback(
        dash.Output({'type' : 'magic-link-collapse-stack', 'index' : dash.MATCH}, 'children'),
        dash.Input({'type'  : 'magic-link-multiselect',    'index' : dash.MATCH}, 'value'),
        dash.State('hikes-info', 'data'),
        dash.State('language', 'data'),
        prevent_initial_call = True
    )
    def magic_link_multiselect_change(
            values     : list[str], 
            hikes_info : dict[str, HikeInfo],
            language   : LANGUAGE
        ) -> list[dict]:
        r'''
        Callback used when one of the elements in one of the multiselect components in the magic link is clicked.

        :param values: checked values of the multiselect
        :param hikes_info: dict of HikeInfo objects with hike names given as keys
        '''

        triggered_id = dash.ctx.triggered_id

        if triggered_id is None: raise dash.exceptions.PreventUpdate

        magic_link = triggered_id['index']
        children   = []

        for pos, hike_name in enumerate(hikes_info.keys()):

            hike_id       = Hikes_table.get_hike_id_from_name(hike_name)
            is_hike_in_db = Magic_links_props_table.is_hike_id_in_magic_link(
                magic_link, hike_id
            )

            # Case when the hike is selected
            if hike_name in values:

                # If the hike is already in the database, we get and apply its color
                if is_hike_in_db:
                    color = Magic_links_props_table.get_color_from_magic_link_and_hike_id(
                        magic_link, hike_id
                    )
                else: color = None

                # Create the component
                children.append(
                    magic_link_hike_element_row(
                        magic_link + '/' + hike_name,
                        hike_name,
                        new_color := (color if color is not None else COLOR_PALETTE[pos]),
                        app.language_handler[language]['magic_link_panel']['item'],
                    )
                )

                # Add hike to the props database if not already there
                if not is_hike_in_db:
                    Magic_links_props_table.insert_row(
                        magic_link,
                        hike_id,
                        new_color
                    )

            # Case when the hike is not selected -> remove the hike from the database if in there
            elif hike_name not in values and is_hike_in_db:

                Magic_links_props_table.delete_row(
                    magic_link, hike_id
                )

        return children

    @app.callback(
        dash.Output({'type' : 'magic-link-hike-row-colorpicker-button',  'index' : dash.MATCH}, 'color'),
        dash.Input({'type'  : 'magic-link-hike-row-colorpicker-picker',  'index' : dash.MATCH}, 'value'),
        prevent_initial_call=True
    )
    def magic_link_colorpicker_selection(
            selected_color  : str,
        ) -> str:
        r'''
        Callback used whenever a color is picked in the colorpicker modal.

        :param selected_color: color corresponding to the colorpicker button clicked in the hike list panel. This is used to setup the default color of the colorpicker when loading

        :returns: color for the colorpicker button
        '''

        triggered_id = dash.ctx.triggered_id

        if triggered_id is None: raise dash.exceptions.PreventUpdate

        # Update the color of the hike in the database
        magic_link, hike_name = triggered_id['index'].split('/')
        hike_id               = Hikes_table.get_hike_id_from_name(hike_name)

        Magic_links_props_table.update_color_in_row(
            selected_color, magic_link, hike_id
        )

        return selected_color

    @app.callback(
        dash.Output('magic-link-container', 'children', allow_duplicate=True),
        dash.Input({'type' : 'magic-link-delete-button',  'index' : dash.MATCH}, 'n_clicks'),
        dash.State('magic-link-container', 'children'),
        running=[
            (dash.Output('add-magic-link', "disabled"), True, False),
            (dash.Output('add-magic-link-tooltip', "disabled"), True, False),
            (dash.Output('magic-link-overlay', "visible"), True, False)
        ],
        prevent_initial_call = True
    )
    def delete_magic_link_button(_, children: list[dict]) -> dash.Patch:
        r'''
        Callback used when one of the delete buttons is clicked.

        :param children: current children (magic link items) of the magic link container
        '''

        triggered_id = dash.callback_context.triggered_id

        if _ is None or triggered_id is None: raise dash.exceptions.PreventUpdate

        pos : None | int = None

        # Delete hike from the magic links table and cascade the delete to the magic links props automatically
        Magic_links_table.delete_row(triggered_id['index'])

        for pos, child in enumerate(children):
            if child['props']['id']['index'] == triggered_id['index']: break

        if pos is None: raise dash.exceptions.PreventUpdate

        out = dash.Patch()
        del out[pos]

        return out

    @app.callback(
        dash.Output("notification-container", 'sendNotifications', allow_duplicate = True),
        dash.Input({'type' : 'magic-link-share', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State('language', 'data'),
        prevent_initial_call = True
    )
    def share_magic_link_button(_, language: LANGUAGE) -> list[Notification]:
        r'''
        Callback used when one of the share magic link buttons is clicked.
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        return [share_hike_notification(app.language_handler[language]['notifications'])]

    return