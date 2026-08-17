import dash_leaflet as     dl
import typing
from   dash_iconify import DashIconify

class DashComplexID(typing.TypedDict):
    r'''
    Class defining the type of complex IDs allowed by Dash for widgets.

    :param type: type of the component
    :param index: identifier of the component
    '''

    type  : str
    index : int | str

DashID = DashComplexID | str

class Dummy(typing.TypedDict):
    r'''
    Class defining a dummy object used to call secondary callbacks after a first callback has finished.

    :param n_clicks: an integer constantly incrementing
    :param type: defines what operation modified the dummy n_clicks value. This is used to filter secondary callbacks.
    '''

    n_clicks : int
    type     : typing.Literal['login', 'upload']

class DummyWithTraces(typing.TypedDict):

    n_clicks : int
    traces   : list[dl.Polyline]

class Notification(typing.TypedDict):
    r'''
    Class defining the content of a notification.
    
    :param title: title of the notification
    :param message: message of the notification
    :param action: whether to show or update the notification
    :param position: position on the screen
    :param color: color of the notification
    :param autoClose: whether the notification should close after X ms
    :param withBorder: whether to draw borders around
    :param icon: icon to add to the notification
    '''

    title           : str
    message         : typing.NotRequired[str]
    action          : typing.Literal['show', 'update']
    position        : typing.Literal['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center']
    color           : str
    autoClose       : typing.NotRequired[int]
    withBorder      : typing.NotRequired[bool]
    withCloseButton : typing.NotRequired[bool]
    icon            : typing.NotRequired[DashIconify]

class ParsedFileContent(typing.TypedDict):
    r'''
    Dictionary class holding data parsed from a GPX or GeoJSON file when loading a hike.
    
    :param distances: distances used to draw the elevation plot
    :param elevations: elevation data used to draw the elevation plot
    :param latitudes: latitude coordinates used to draw the path on the map and for the marker
    :param longitudes: longitude coordinates used to draw the path on the map and for the marker
    '''

    distances             : list[float]
    elevations            : list[float]
    latitudes             : list[float]
    longitudes            : list[float]

class HikeDataForMarker(typing.TypedDict):
    r'''Dictionary class holding latitude and longitude information to move the marker on the map when hovering over the elevation plot.'''

    latitudes  : list[float]
    longitudes : list[float]

class HikeDataForElevationPlot(typing.TypedDict):
    r'''Dictionary class holding distances and elevations information a single hike.'''

    distances  : list[float]
    elevations : list[float]

class HikeProps(typing.TypedDict):
    r'''Dictionary class holding the name of a hike and its associated color.'''

    name  : str
    color : str

class HikeInfo(typing.TypedDict):
    r'''
    Dictionary class holding all the information relative to a single hike.
    
    :param center_lat: latitude of the center of the hike
    :param center_lon: longitude of the center of the hike
    :param distances: list of distances for the elevation plot
    :param elevations: list of elevation data for the elevation plot
    :param latitudes: latitude coordinates used to draw the path on the map and for the marker
    :param longitudes: longitude coordinates used to draw the path on the map and for the marker
    :param color: color of the hike
    '''

    center_lat : float
    center_lon : float
    distances  : list[float]
    elevations : list[float]
    latitudes  : list[float]
    longitudes : list[float]
    color      : str

EMPTY_HIKE_DATA_FOR_PLOT : typing.Final = HikeDataForElevationPlot(
    distances  = [],
    elevations = []
)

EMPTY_HIKE_DATA_FOR_MAP : typing.Final = HikeDataForMarker(
    latitudes  = [],
    longitudes = []
)