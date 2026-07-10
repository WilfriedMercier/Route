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

def calculate_zoom_from_bounds(bounds, map_width=800, map_height=600):
    """
    Calculate optimal zoom level from bounding box.
    
    Args:
        bounds: [[lat_southwest, lng_southwest], [lat_northeast, lng_northeast]]
        map_width: Map container width in pixels
        map_height: Map container height in pixels
    
    Returns:
        int: Optimal zoom level (1-19)
    """
    if len(bounds) != 2:
        return 10  # Default zoom
    
    sw_lat, sw_lng = bounds[0]
    ne_lat, ne_lng = bounds[1]
    
    # Calculate latitude and longitude differences
    lat_diff = abs(ne_lat - sw_lat)
    lng_diff = abs(ne_lng - sw_lng)
    
    # Avoid division by zero
    if lat_diff == 0 or lng_diff == 0:
        return 15  # High zoom for very small areas
    
    # Average latitude for longitude correction (cosine factor)
    avg_lat = (sw_lat + ne_lat) / 2
    
    # Convert degrees to approximate kilometers
    # 1 degree latitude ≈ 111.32 km (varies slightly but consistent enough)
    lat_km = lat_diff * 111.32
    # Longitude distance varies with latitude
    lng_km = lng_diff * 111.32 * math.cos(math.radians(avg_lat))
    
    # Use the larger dimension (with padding buffer)
    max_dist_km = max(lat_km, lng_km) * 1.2  # 20% padding
    
    # World circumference at equator in km
    world_circumference = 40075
    
    # Map dimensions (use the smaller dimension for conservative calculation)
    map_size = min(map_width, map_height)
    
    # Pixels per degree at zoom 0
    pixels_per_degree_at_zoom0 = 256 / 360  # 256 tiles / 360 degrees
    
    # Calculate zoom level
    # Formula derived from Mercator projection and tile system
    zoom = math.log2(
        (world_circumference * map_size) / (max_dist_km * 360)
    )
    
    # Clamp to valid Leaflet range (1-19) and round down
    return max(1, min(19, int(zoom)))