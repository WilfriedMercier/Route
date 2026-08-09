import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

def magic_link_panel_layout(language_handler: dict) -> dmc.Drawer:

    add_magic_link_button = dmc.Button(
        language_handler['add_button']['text'],
        leftSection = DashIconify(icon='gg:add'),
        variant     = 'outline',
        fullWidth   = True,
    )

    return dmc.Drawer(
        add_magic_link_button,
        withCloseButton = True,
        title           = language_handler['title'],
        id              = 'magic-link-panel-modal', 
    )