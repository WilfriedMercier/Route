import os
import gpxpy
import base64
import pathlib
import os

from .logic import (
    calculate_distance_from_coords, 
    calculate_elevation_stats, 
    extract_elevation_data_from_gpx,
    zoom_for_bounds
)

def process_hike(filename: str, content: str) -> dict[str, dict] | None:
    """Load hike files from the hikes directory and parse them."""

    # Load the GPX file and extract coordinates and elevations
    if filename.endswith('.gpx'): 

        gpx                = gpxpy.parse(content)
        coords, elevations = extract_elevation_data_from_gpx(gpx)
    
    else: 
        print(f"Unsupported file format for {filename}, skipping.")
        return
                
    # Compute cumulative distances
    distances = calculate_distance_from_coords(coords)

    # Compute bounds for the hike (min/max lat/lon)
    lats   = [coord[0] for coord in coords]
    lons   = [coord[1] for coord in coords]
    bounds = ((min(lats), min(lons)), (max(lats), max(lons)))

    # Compute estimated zoom level for the hike
    zoom   = zoom_for_bounds(bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1])

    # Compute center of the hike
    center = (bounds[0][0] + (bounds[1][0] - bounds[0][0]) / 2, bounds[0][1] + (bounds[1][1] - bounds[0][1]) / 2)

    # Compute elevation stats (None if invalid)
    stats  = calculate_elevation_stats(elevations)
    
    # Add the total distance to the stats
    if stats is not None: 
        stats['total_distance_km'] = distances[-1]
    else: 
        stats = {'total_distance_km': distances[-1]}
                
    hike_data = {
        'lon'        : lons,
        'lat'        : lats,
        'type'       : 'gpx',
        'distances'  : distances,
        'bounds'     : bounds,
        'zoom'       : zoom,
        'center'     : center,
        'elevations' : elevations,
        'stats'      : stats
    }

    return hike_data
                
def parse_uploaded_file(content: str, filename: str) -> tuple[str, dict[str, dict] | None]:

    _, content_string = content.split(',')
    decoded           = base64.b64decode(content_string).decode('utf-8')
    properties        = process_hike(filename, str(decoded))

    return filename, properties

"""
    hikes_data[pathlib.Path(filename).stem] = hike_data
                
except Exception as e: print(f"Error loading {filename}: {str(e)}")
    
    # Add a default color to each hike by looping through a color palette
    for pos, hike_name in enumerate(hikes_data.keys()):
        hikes_data[hike_name]['color'] = COLOR_PALETTE[pos]

    return dict(sorted(hikes_data.items()))
"""