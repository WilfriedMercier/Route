import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

def magic_link_panel_layout(language_handler: dict) -> dmc.Drawer:

    add_magic_link_button = dmc.Button(
        language_handler['add_button']['text'],
        leftSection = DashIconify(icon='gg:add'),
        variant     = 'outline',
        fullWidth   = True,
    )

    magic_link_list = magic_link_container()

    return dmc.Drawer(
        [
            add_magic_link_button,
            magic_link_list
        ],
        withCloseButton = True,
        title           = language_handler['title'],
        id              = 'magic-link-panel', 
        opened=True
    )

def magic_link_container_item(name: str) -> dmc.Stack:

    control = dmc.Group(
        [
            dmc.TextInput(name, readOnly=True, style={'flex' : 1}),
            dmc.Button(
                DashIconify(icon='mdi:chevron-down'),
                id        = {'type' : 'magic-link-collapse-button', 'index' : name},
                className = 'magic_link_collapse_button',
                variant   = 'subtle'
            )
        ],
    )

    panel = dmc.Collapse(
        dmc.Text('test'), 
        id={'type' : 'magic-link-collapse', 'index' : name},
        style = {
            'padding' : '5px',
            'margin'  : '5px',
        }
    )

    return dmc.Stack(
        [control, panel],
        style={
        'backgroundColor' : 'var(--custom-ht-background)',
        'padding' : '5px',
        'margin-bottom' : '10px',
    })

def magic_link_container() -> dmc.Stack:

    children = [
        magic_link_container_item('Magic link #1'),
        magic_link_container_item('Magic link #2')
    ]

    return dmc.Stack(
        children,
        gap = 10,
        style={'margin-top' : '20px', 'margin-bottom' : '20px'}
    )