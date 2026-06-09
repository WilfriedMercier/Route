import os
import pathlib
import gpxpy
from   plotly.colors import qualitative

COLOR_PALETTE = qualitative.Plotly

from .logic import (
    calculate_distance_from_coords, 
    calculate_elevation_stats, 
    extract_elevation_data_from_gpx,
    zoom_for_bounds
)

def load_hikes_from_directory() -> dict[str, dict]:
    """Load hike files from the hikes directory and parse them."""

    hikes_dir  = pathlib.Path("hikes")
    hikes_data = {}
    
    if not hikes_dir.exists(): return hikes_data
    
    # Loop through files in the hikes directory
    for filename in os.listdir(hikes_dir):
        if filename.endswith(('.json', '.geojson', '.gpx')):

            file_path = hikes_dir / filename

            # Try to load the file and extract data
            try:

                # Load the GPX file and extract coordinates and elevations
                if filename.endswith('.gpx'): 
                     coords, elevations = load_gpx_file(file_path)
                else: 
                    print(f"Unsupported file format for {filename}, skipping.")
                    continue
                
                # Compute cumulative distances
                distances = calculate_distance_from_coords(coords)

                # Compute bounds for the hike (min/max lat/lon)
                lats   = [coord[0] for coord in coords]
                lons   = [coord[1] for coord in coords]
                bounds = ((min(lats), min(lons)), (max(lats), max(lons)))

                # Compute estimated zoom level for the hike
                zoom   = zoom_for_bounds(bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1])

                # Compute center of the hike
                center    = (bounds[0][0] + (bounds[1][0] - bounds[0][0]) / 2, bounds[0][1] + (bounds[1][1] - bounds[0][1]) / 2)

                # Compute elevation stats (None if invalid)
                stats  = calculate_elevation_stats(elevations)
                
                # Add the total distance to the stats
                if stats is not None: 
                    stats['total_distance_km'] = distances[-1]
                else: 
                    stats = {'total_distance_km': distances[-1]}
                            
                hike_data = {
                    'coords'     : coords,
                    'type'       : 'gpx',
                    'distances'  : distances,
                    'bounds'     : bounds,
                    'zoom'       : zoom,
                    'center'     : center,
                    'elevations' : elevations,
                    'stats'      : stats
                }
                            
                hikes_data[pathlib.Path(filename).stem] = hike_data
                            
            except Exception as e: print(f"Error loading {filename}: {str(e)}")
    
    # Add a default color to each hike by looping through a color palette
    for pos, hike_name in enumerate(hikes_data.keys()):
        hikes_data[hike_name]['color'] = COLOR_PALETTE[pos]

    return dict(sorted(hikes_data.items()))

def load_gpx_file(file_path: pathlib.Path) -> tuple[list[tuple[float, float]], list[float]]:
    """
    Load a GPX file and extract coordinates and elevations.
    
    :param file_path: Path to the GPX file.
    :return: Tuple of (coords, elevations).
    """

    with open(file_path, 'r') as f: gpx = gpxpy.parse(f)

    return extract_elevation_data_from_gpx(gpx)