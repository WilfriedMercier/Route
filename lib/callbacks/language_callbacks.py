import dash
import plotly.graph_objects as     go
from   textwrap             import dedent
from   flask                import session

from ..components.misc import language_element
from ..lang            import LANGUAGE

def register_language_callacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that update the language of the UI

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    '''

    @app.callback(
        dash.Output('language', 'data', allow_duplicate=True),

        dash.Output('theme-toggle-tooltip', 'label'),
        dash.Output('hike-panel-button', 'children'),
        dash.Output('hike-panel-button-tooltip', 'label'),
        dash.Output('hall-of-fame-button', 'children'),
        dash.Output('hall-of-fame-button-tooltip', 'label'),
        dash.Output('hike-panel', 'title'),

        dash.Output({'type' : 'hikelist-delete-button-tooltip', 'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-hide-button-tooltip',   'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',   'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-share-button-tooltip',  'index' : dash.ALL}, 'label'),
        dash.Output('upload-hike-button', 'children'),

        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output('login-modal', 'title'),
        dash.Output('login-modal-id-input', 'label'),
        dash.Output('login-modal-id-input', 'placeholder'),
        dash.Output('login-modal-password-input', 'label'),
        dash.Output('login-modal-password-input', 'placeholder'),
        dash.Output('send-login-button', 'children'),

        dash.Output({'type' : 'language-dropdown', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output('magic-link-modal-text', 'children'),
        dash.Output('magic-link-modal', 'title'),

        dash.Output('elevation-plot', 'figure', allow_duplicate=True),
  
        dash.Input({'type': 'language-button', 'index': dash.ALL}, 'n_clicks'),
        dash.State('number-hikes', 'data'),
        dash.State('elevation-plot', 'figure'),

        prevent_initial_call=True,
    )
    def language_selection(n_clicks, n_hikes: int, ev_plot) -> tuple[
        str, 
        str, str, str, str, str, str,
        list[str], list[str], list[str], list[str], tuple[str],
        tuple[str, dash.NoUpdate] | tuple[dash.NoUpdate, dash.NoUpdate], tuple[str, str],
        str, str, str, str, str, str,
        tuple[list, list],
        str, str,
        go.Figure
    ]:
        r'''
        Callback used when the language of the application is changed.

        :param n_clicks: which language was selected
        :param n_hikes: total number of hike elements
        '''

        if all(i is not None for i in n_clicks): raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id

        if not isinstance(triggered_id, dict): raise dash.exceptions.PreventUpdate

        lang : LANGUAGE = triggered_id['index'].split('-')[-1]
        translation     = app.language_handler[lang]

        login_button_text    = translation['login_logout_buttons']['login']['text'] if 'user_id' not in session else dash.no_update
        login_button_tooltip = translation['login_logout_buttons']['logout' if 'user_id' in session else 'login']['tooltip']
        
        language_dropdown = [
            language_element(
                triggered_id['index'],
                app.language_handler.map_language_to_dropdown_text(selected_lang),
                selected_lang,
                selected_lang == lang
            )
            for selected_lang in app.language_handler.languages
        ]

        # Update the elevation plot with the right translation
        fig = go.Figure(ev_plot)
        fig.update_layout(
            xaxis_title = translation['elevation_plot']['xlabel'],
            yaxis_title = translation['elevation_plot']['ylabel']
        )

        fig.update_traces(
            hovertemplate=dedent(f'''\
                <extra></extra>
                <b>{translation['elevation_plot']['hovertemplate']['distance']}:</b> %{{x:.1f}} km<br>
                <b>{translation['elevation_plot']['hovertemplate']['remaining_distance']}:</b> %{{customdata[0]:.1f}} km<br>
                <b>{translation['elevation_plot']['hovertemplate']['elevation']}:</b> %{{y:.0f}} m<br>
                <b>{translation['elevation_plot']['hovertemplate']['slope']}:</b> %{{customdata[1]:.1f}}%
            ''')
        )

        return (
            lang,
            translation['topbar']['theme_switcher']['tooltip'],
            translation['menubar']['hike_panel_button']['text'],
            translation['menubar']['hike_panel_button']['tooltip'],
            translation['menubar']['hall_of_fame_button']['text'],
            translation['menubar']['hall_of_fame_button']['tooltip'],
            translation['hike_panel']['title'],

            [translation['hike_panel']['delete_button']['tooltip']] * n_hikes,
            [translation['hike_panel']['hide_button'][  'tooltip']] * n_hikes,
            [translation['hike_panel']['colorpicker'][  'tooltip']] * n_hikes,
            [translation['hike_panel']['share_button'][ 'tooltip']] * n_hikes,
            (translation['hike_panel']['upload_button']['text'],),

            (login_button_text, login_button_text),
            (login_button_tooltip, login_button_tooltip),

            translation['login_modal']['title'],
            translation['login_modal']['user_id_input']['label'],
            translation['login_modal']['user_id_input']['placeholder'],
            translation['login_modal']['user_password_input']['label'],
            translation['login_modal']['user_password_input']['placeholder'],
            translation['login_modal']['send_login_button']['text'],

            (language_dropdown, language_dropdown),

            translation['magic_link_modal']['text'],
            translation['magic_link_modal']['title'],

            fig
        )
    
    return