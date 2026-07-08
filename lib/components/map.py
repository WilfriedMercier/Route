import dash_mantine_components   as     dmc
import dash_leaflet              as     dl

from ..lang import LanguageHandler, LANGUAGE

def elevation_plot_layout(language_dict: dict) -> dmc.LineChart:

    fig = dmc.LineChart(
        data           = [], # type: ignore
        dataKey        = 'x',
        curveType      = "Monotone"    , # type: ignore
        series         = [{'name' : 'y', 'color' : 'var(--custom-primary-color)'}], # type: ignore
        withDots       = False,
        strokeWidth    = 3,
        connectNulls   = True,
        h              = '30%',
        xAxisLabel     = 'Distance (km)',
        yAxisProps={'domain' : [0, 1000]},
        yAxisLabel     = 'Elevation (m)',
        withTooltip    = True,
        tooltipProps   = {'content': {'function': 'CustomTooltip'}},
        style          = {'display' : 'none'},
        id             = 'elevation-plot'
    )

    return fig

def map_page_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.AppShellMain:
    r'''
    Widget containing the main content area of the application which contains the map and the elevation plot.
    
    :param language_handler: object the translation of the UI
    :param language: language used at startup
    '''
       
    map            = generate_leaflet_map_figure()
    elevation_plot = elevation_plot_layout(language_handler[language]['elevation_plot'])

    return dmc.AppShellMain(
            dmc.Stack([map, elevation_plot], id = 'map-page'),
        style = {'width' : '100%', 'height' : '100vh'},
        id = 'appshell-main'
    )

def generate_leaflet_map_figure(
        lon  : float | None = None, 
        lat  : float | None = None,
        zoom : int   | None = None
    ) -> dl.Map:
    r'''
    Generate an empty leaflet figure serving as baseline every time the map has to be updated.

    :param lon: center's longitude
    :param lat: center's latitude
    :param zoom: zoom level
    '''

    if lon is None  : lon  = 4.8357
    if lat is None  : lat  = 45.7640
    if zoom is None : zoom = 10

    layer_control = generate_layer_control()

    figure = dl.Map(
        children = [
            layer_control,
            dl.FullScreenControl(),
            dl.ScaleControl(position="bottomright"),
            dl.MeasureControl(
                position          = "topleft",
                primaryLengthUnit = "kilometers",
                primaryAreaUnit   = "hectares",
                activeColor       = "#214097",
                completedColor    = "#972158",
            ),
        ],
        center   = [lat, lon],  # type: ignore
        zoom     = zoom,
        id       = 'map', 
        style    = {'zIndex': 0},
    ) # type: ignore
    
    return figure

def generate_base_layers() -> list[dl.BaseLayer | dl.LayerGroup]:
    r'''Generate the base layers used as map background.'''

    return [
        dl.BaseLayer(
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", attribution='© OpenStreetMap contributors'),
            name    = "OSM", # type: ignore
            checked = True
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attribution='© OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
            name    = "Open topo", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}.png', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Stamen toner", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg', attribution='© Stadia Maps © Stamen Design © OpenStreetMap contributors '),
            name    = "Stamen watercolor", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Stamen terrain", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Satellite", # type: ignore
            checked = False
        ),

    ]

def generate_layer_control(poly_lines: list[dl.Polyline] = []) -> dl.LayersControl:
    r'''
    Generate the layer control that contains map styles and hike paths.

    :param poly_lines: hike paths to show on the map
    '''

    layers = generate_base_layers()
    layers.append(dl.LayerGroup(poly_lines, id='map-polylines'))

    return dl.LayersControl(
        layers,
        position = "topright",
        id       = 'map-layer-control'
    )