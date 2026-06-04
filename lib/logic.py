import math

def extract_elevation_data_from_gpx(gpx) -> tuple[list[tuple[float, float]], list[float]]:
    """
    Extract elevation data from GPX file (tracks and waypoints).
    
    :param gpx: GPX file object.
    :return: Tuple of (coords, elevations).
    """

    coords     = []
    elevations = []
    
    # Extract from tracks
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                
                coords.append((point.latitude, point.longitude))
                elevations.append(point.elevation)
    
    # Extract from waypoints if no track data
    if not coords and gpx.waypoints:
        for point in gpx.waypoints:
            
            coords.append((point.latitude, point.longitude))
            elevations.append(point.elevation)
    
    return coords, elevations

def calculate_distance_from_coords(points):
    """
    Calculate cumulative distance along a path (in km).
    
    :param points: List of (latitude, longitude) tuples.
    :return: List of cumulative distances at each point.
    """
        
    distances      = [0.0]
    total_distance = 0.0
    
    for i in range(1, len(points)):

        lat1, lon1 = math.radians(points[i-1][0]), math.radians(points[i-1][1])
        lat2, lon2 = math.radians(points[i][0]), math.radians(points[i][1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_km = 6371 * c  # Earth's radius in km
        
        total_distance += distance_km
        distances.append(total_distance)
    
    return distances

def calculate_elevation_stats(elevations: list[float]) -> dict[str, float] | None:
    """
    Calculate elevation statistics.
    
    :param elevations: List of elevation values.
    :return: Dictionary with elevation statistics or None if data is invalid.
    """

    if not check_elevation_data(elevations): return None

    min_elev       = min(elevations)
    max_elev       = max(elevations)
    elevation_gain = 0
    elevation_loss = 0
    
    for i in range(1, len(elevations)):

        diff = elevations[i] - elevations[i-1]

        if diff > 0: elevation_gain += diff
        else       : elevation_loss += abs(diff)
    
    return {
        'min': min_elev,
        'max': max_elev,
        'gain': elevation_gain,
        'loss': elevation_loss
    }

def check_elevation_data(elevations: list[float]) -> bool:
    """
    Check if elevation data is valid (all non-zero and non-negative).
    
    :param elevations: List of elevation values.
    :return: True if valid, False otherwise.
    """

    return all(e is not None and e > 0 for e in elevations)

def zoom_for_bounds(south: float, west: float, north: float, east: float) -> int:
    r'''Estimate a starting zoom level that fits the given geographic bounds.'''


    lat_diff = max(0.0001, abs(north - south))
    lon_diff = max(0.0001, abs(east - west))
    max_diff = max(lat_diff, lon_diff)

    # Convert the longitudinal span into a map zoom level.
    zoom = int(math.floor(math.log2(360 / max_diff)))

    return zoom