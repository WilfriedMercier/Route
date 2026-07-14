from typing       import TypedDict, Final, NotRequired, Literal
from dash_iconify import DashIconify

class Notification(TypedDict):
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
    message         : NotRequired[str]
    action          : Literal['show', 'update']
    position        : Literal['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center']
    color           : str
    autoClose       : NotRequired[int]
    withBorder      : NotRequired[bool]
    withCloseButton : NotRequired[bool]
    icon            : NotRequired[DashIconify]

class ParsedFileContent(TypedDict):
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

class HikeDataForMarker(TypedDict):
    r'''Dictionary class holding latitude and longitude information to move the marker on the map when hovering over the elevation plot.'''

    latitudes  : list[float]
    longitudes : list[float]

class HikeDataForElevationPlot(TypedDict):
    r'''Dictionary class holding distances and elevations information a single hike.'''

    distances  : list[float]
    elevations : list[float]

class HikeProps(TypedDict):
    r'''Dictionary class holding the name of a hike and its associated color.'''

    name  : str
    color : str

class HikeInfo(TypedDict):
    r'''
    Dictionary class holding all the information relative to a single hike.
    
    :param center_lat: latitude of the center of the hike
    :param center_lon: longitude of the center of the hike
    :param zoom: zoom level
    :param distances: list of distances for the elevation plot
    :param elevations: list of elevation data for the elevation plot
    :param latitudes: latitude coordinates used to draw the path on the map and for the marker
    :param longitudes: longitude coordinates used to draw the path on the map and for the marker
    '''

    center_lat            : float
    center_lon            : float
    zoom                  : int | float
    distances             : list[float]
    elevations            : list[float]
    latitudes             : list[float]
    longitudes            : list[float]

EMPTY_HIKE_DATA_FOR_PLOT : Final = HikeDataForElevationPlot(
    distances  = [],
    elevations = []
)

EMPTY_HIKE_DATA_FOR_MAP : Final = HikeDataForMarker(
    latitudes  = [],
    longitudes = []
)