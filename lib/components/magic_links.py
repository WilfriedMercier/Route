import dash_mantine_components as dmc

from .misc   import custom_colorpicker
from ..misc  import COLOR_PALETTE
from ..icons import (
    IconAdd,
    IconChevronDown,
    IconDelete,
    IconList,
    IconEdit,
    IconShare
)

def magic_link_panel_layout(language_handler: dict) -> dmc.Drawer:
    r'''
    Panel containing magic links.

    :param language handler: current language of the UI
    '''

    add_magic_link_button = dmc.ActionIcon(
        IconAdd(), 
        id      = 'add-magic-link',
        variant = 'subtle',
    )

    add_magic_link_button_tooltip = dmc.Tooltip(
        add_magic_link_button,
        id    = 'add-magic-link-tooltip',
        label = language_handler['add_button']['tooltip']
    )

    magic_link_list = magic_link_container(language_handler['item'])

    loading_overlay = dmc.LoadingOverlay(
        id           = 'magic-link-overlay',
        visible      = False,
        overlayProps = {"radius": "sm", "blur": 2},
        zIndex       = 10,
    )

    return dmc.Drawer(
        [loading_overlay, magic_link_list],
        withCloseButton = True,
        title           = dmc.Group([
            language_handler['title'],
            add_magic_link_button_tooltip
        ]),
        id              = 'magic-link-panel',
        opened = True
    )

def magic_link_container(language_handler: dict) -> dmc.Stack:
    r'''
    Container with all magic links.

    :param language handler: current language of the UI elements associated to this container
    '''

    return dmc.Stack(
        [],
        id    = 'magic-link-container',
        gap   = 10,
        style = {'marginTop' : '20px', 'marginBottom' : '20px'},
    )

def magic_link_container_item(
        magic_link: str, 
        name: str, 
        language_handler: dict,
        hike_names : list[str] = []
    ) -> dmc.Stack:
    r'''
    Container with all magic links.

    :param magic_link: magic link used as a unique identifier for all the components
    :param name: name of the magic link shown by default 
    :param language handler: current language of the UI elements associated to this container
    :param hike_names: list containing the names of the hikes shown in the multiselect widget
    '''

    delete_button = dmc.ActionIcon(
        IconDelete(),
        id      = {'type' : 'magic-link-delete-button', 'index' : magic_link},
        variant = 'subtle'
    )

    delete_button_tooltip = dmc.Tooltip(
        delete_button,
        label = language_handler['delete_button']['tooltip']
    )

    edit_title_button = dmc.ActionIcon(
        IconEdit(),
        variant = 'subtle',
        id      = {'type' : 'magic-link-collapse-title-edit-button', 'index' : magic_link}
    )

    edit_title_button_tooltip = dmc.Tooltip(
        edit_title_button,
        label = language_handler['edit_title_button']['edit']['tooltip']
    )

    title = dmc.TextInput(
        name, 
        readOnly     = True,
        rightSection = edit_title_button_tooltip,
        className    = 'magic-link-collapse-title',
        styles       = {'input' : {'backgroundColor': 'transparent', 'cursor' : 'default'}},
        id           = {'type' : 'magic-link-collapse-title', 'index' : magic_link}
    )

    share_button = dmc.ActionIcon(
        IconShare(),
        id      = {'type' : 'magic-link-share', 'index' : magic_link},
        variant = 'subtle'
    )

    share_button_tooltip = dmc.Tooltip(
        share_button,
        label = language_handler['share_button']['tooltip']
    )

    multiselect = dmc.MultiSelect(
        id                = {'type' : 'magic-link-multiselect', 'index' : magic_link},
        className         = 'magic-link-multiselect',
        withAlignedLabels = True,
        withCheckIcon     = True,
        openOnFocus       = True,
        searchable        = False,
        clearable         = False,
        data = [
            {'value' : name, 'label' : name}
            for name in hike_names
        ],
        value         = [],
        comboboxProps = {'width' : '300px'},
        rightSection  = IconList(),
        variant       = 'subtle'
    )

    multiselect_tooltip = dmc.Tooltip(
        multiselect,
        label = language_handler['list_button']['tooltip']
    )

    collapse_button = dmc.ActionIcon(
        IconChevronDown(),
        id        = {'type' : 'magic-link-collapse-button', 'index' : name},
        className = 'magic_link_collapse_button',
        variant   = 'subtle'
    )

    collapse_button_tooltip = dmc.Tooltip(
        collapse_button,
        label = language_handler['collapse_button']['tooltip'],
    )

    # Header-like part always shown
    control = dmc.Group([
        delete_button_tooltip, 
        title, 
        share_button_tooltip, 
        multiselect_tooltip, 
        collapse_button_tooltip
    ])

    # Elements shown in the collapsible area
    rows = dmc.Stack(
        [
            magic_link_hike_element_row(
                magic_link + '/' + hike_name, 
                hike_name,
                COLOR_PALETTE[pos], 
                language_handler
            )
            for pos, hike_name in enumerate(hike_names)
        ]
    )

    # Collapsible area
    panel = dmc.Collapse(
        rows, 
        id    = {'type' : 'magic-link-collapse', 'index' : name},
        style = {
            'padding' : '5px',
            'margin'  : '5px',
        }
    )

    return dmc.Stack(
        [control, panel],
        id    = {'type' : 'magic-link-container-item', 'index' : magic_link},
        style = {
        'backgroundColor' : 'var(--custom-ht-background)',
        'padding' : '5px',
        'margin-bottom' : '10px',
        'borderRadius' : '5px'
    })

def magic_link_hike_element_row(
        index            : str,
        hike_name        : str,
        color            : str, 
        language_handler : dict
    ) -> dmc.Group:

    colorpicker = dmc.Tooltip(
        custom_colorpicker(
            color, 
            {'type' : 'magic-link-colorpicker-button',  'index' : index},
            {'type' : 'magic-link-colorpicker-picker',  'index' : index},
            {'type' : 'magic-link-colorpicker-popover', 'index' : index}
        ),
        label     = language_handler['collapse']['colorpicker']['tooltip'],
        id        = {'type' : 'magic-link-hike-colorpicker-tooltip', 'index' : index}
    )

    label = dmc.Text(hike_name)

    return dmc.Group(
        [colorpicker, label], 
        id        = {'type' : 'magic-link-row', 'index' : index},
        className = 'magic-link-hike-element-row-group', 
        display   = 'none'
    )