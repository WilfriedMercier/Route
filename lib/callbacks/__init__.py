import dash

from   .login_callbacks        import register_login_callbacks
from   .clientside_callbacks   import register_clientside_callbacks
from   .keydown_callbacks      import register_keydown_callbacks
from   .magic_link_callbacks   import register_magic_link_panel_callbacks
from   .burger_callbacks       import register_burger_callbacks
from   .language_callbacks     import register_language_callacks
from   .menubar_callbacks      import register_menubar_callbacks
from   .hike_drawer_callbacks  import register_hike_drawer_callbacks
from   .upload_hike_callbacks  import register_upload_hike_callbacks
from   .ui_init_callbacks      import register_ui_init_callbacks
from   .delete_modal_callbacks import register_validate_modal_callbacks

def register_callbacks(app : dash.Dash) -> None:
    r'''
    Register all callbacks.

    :param app: dash application
    '''

    register_burger_callbacks(app)
    register_clientside_callbacks(app)
    register_hike_drawer_callbacks(app)
    register_keydown_callbacks(app)
    register_language_callacks(app)
    register_login_callbacks(app)
    register_magic_link_panel_callbacks(app)
    register_menubar_callbacks(app)
    register_ui_init_callbacks(app)
    register_upload_hike_callbacks(app)
    register_validate_modal_callbacks(app)

    return