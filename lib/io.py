import gpxpy
import base64
import pathlib
import json

from   .errors import UnsupportedFileFormatError, GeoJsonParsingFailed
from   .types  import HikeInfo, ParsedFileContent
from   .logic  import calculate_distance_from_coords

from .logic import calculate_distance_from_coords

def process_hike(filename: str, content: str) -> HikeInfo:
    r"""
    Load hike files from the hikes directory and parse them.
    
    :param filename: name of the file (including extension)
    :param content: decoded content of the file

    :returns: a `HikeInfo` object containing information about the processed hike
    """

    # Load the GPX file and extract coordinates and elevations
    if filename.endswith('.gpx'): 
        info = process_gpx_file(content)
    elif filename.endswith('.geojson'):
        info = process_geojson_file(content)
    
    else: raise UnsupportedFileFormatError(f"Unsupported file format for {filename}, skipping.")

    # Compute bounds for the hike (min/max lat/lon)
    bounds = (
        (min(info['latitudes']), min(info['longitudes'])), 
        (max(info['latitudes']), max(info['longitudes']))
    )

    # Extract longitude and latitude info

    # Compute center of the hike
    center = (bounds[0][0] + (bounds[1][0] - bounds[0][0]) / 2, bounds[0][1] + (bounds[1][1] - bounds[0][1]) / 2)
                
    hike_data = HikeInfo(
        longitudes            = info['longitudes'],
        latitudes             = info['latitudes'],
        distances             = info['distances'],
        elevations            = info['elevations'],
        center_lat            = center[0],
        center_lon            = center[1],
    )

    return hike_data

def process_gpx_file(content: str) -> ParsedFileContent:
    r'''
    Process GPX files.

    :param content: content of the GPX file

    :returns: tuple with
        - list of (lat, lon) coordinates
        - list of corresponding elevations    
    '''

    gpx        = gpxpy.parse(content)
    
    latitudes  = []
    longitudes = []
    elevations = []
    
    # Extract from tracks
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                
                latitudes.append(point.latitude)
                longitudes.append(point.longitude)
                elevations.append(point.elevation)
    
    # Extract from waypoints if no track data
    if (latitudes == [] or longitudes == []) and gpx.waypoints:
        for point in gpx.waypoints:
            
            latitudes.append(point.latitude)
            longitudes.append(point.longitude)
            elevations.append(point.elevation)

    return ParsedFileContent(
        latitudes             = latitudes,
        longitudes            = longitudes,
        elevations            = elevations,
        distances             = calculate_distance_from_coords(latitudes, longitudes)
    )

def process_geojson_file(content: str) -> ParsedFileContent:
    r'''
    Process GeoJSON files.

    :param content: content of the GeoJSON file

    :returns: tuple with
        - list of (lat, lon) coordinates
        - list of corresponding elevations    
    '''

    data = json.loads(content)

    if (
        'data'           not in data or
        'elevationData'  not in data['data'] or
        'coordinates'    not in data['data']['elevationData'] or
        'elevationData'  not in data['data']['elevationData'] or
        'profileLngLats' not in data['data']['elevationData']
    ): raise GeoJsonParsingFailed

    # Extract latitude and longitude data 
    latitudes  = []
    longitudes = []
    for coord in data['data']['elevationData']['profileLngLats']:
        latitudes.append( coord[1])
        longitudes.append(coord[0])

    # Extract distance and elevation data
    distances  = []
    elevations = []
    for row in data['data']['elevationData']['elevationData']:
        distances.append( row['x'])
        elevations.append(row['y'])

    return ParsedFileContent(
        latitudes  = latitudes,
        longitudes = longitudes,
        elevations = elevations,
        distances  = distances,
    )
                
def decode_and_process_uploaded_file(content: str, filename: str) -> tuple[str, HikeInfo]:
    r'''
    Given a filename and its encoded content, parse it and return its name and properties.

    :param content: encoded content of the file
    :param filename: name of the file

    :returns: a tuple with the name of the file without its extension and the associated `HikeInfo` object
    '''

    _, content_string = content.split(',')
    decoded           = base64.b64decode(content_string).decode('utf-8')
    properties        = process_hike(filename, str(decoded))

    return pathlib.Path(filename).stem, properties