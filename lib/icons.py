import functools
from   dash_iconify import DashIconify

_width = 20

# Up and down chevrons
IconChevronUp   = functools.partial(DashIconify, icon='mdi:chevron-up',  width=_width)
IconChevronDown = functools.partial(DashIconify, icon='mdi:chevron-down', width=_width)

# Check mark
IconCheck       = functools.partial(DashIconify, icon='material-symbols:check', width=_width)

# Edit symbol
IconEdit        = functools.partial(DashIconify, icon='material-symbols:edit-outline', width=_width)

# Delete symbol
IconDelete      = functools.partial(DashIconify, icon='material-symbols:delete', width=_width)

# List symbol
IconList        = functools.partial(DashIconify, icon="material-symbols:list", width=_width)

# Add icon
IconAdd         = functools.partial(DashIconify, icon='gg:add', width=_width)

# Share icon
IconShare       = functools.partial(DashIconify, icon='material-symbols:share', width=_width)

# Visible/invisible (eye) icons
IconVisible     = functools.partial(DashIconify, icon='streamline:visible', width=_width)
IconInvisible   = functools.partial(DashIconify, icon='streamline:invisible-1', width=_width)

# Sun/Moon icons for the theme switch toggle
IconSun         = functools.partial(DashIconify, icon='radix-icons:sun',  width=_width, color = 'darkorange')
IconMoon        = functools.partial(DashIconify, icon='radix-icons:moon', width=_width, color = 'lightblue')

# Language icon
IconLanguage    = functools.partial(DashIconify, icon='mdi:language',  width=_width)

# User icon
IconUser        = functools.partial(DashIconify, icon='mdi:user',  width=_width)

# Hiker icon
IconHiker       = functools.partial(DashIconify, icon='gis:hiker',  width=_width)

# Achievement icon
IconAchieve     = functools.partial(DashIconify, icon='mdi:achievement-outline',  width=_width)

# Error icon
IconError       = functools.partial(DashIconify, icon='si:error-duotone', width=_width)

# Success icon
IconSuccess     = functools.partial(DashIconify, icon='icon-park-outline:success', width=_width)