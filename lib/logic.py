import math

def calculate_distance_from_coords(latitudes: list[float], longitudes: list[float]) -> list[float]:
    """
    Calculate cumulative distance along a path (in km).
    
    :param latitudes: list of latitude coordinates
    :param longitudes: list of longitude coordinates

    :return: list of cumulative distances at each point.
    """
        
    distances      = [0.0]
    total_distance = 0.0
    
    for i in range(1, len(latitudes)):

        lat1, lon1 = math.radians(latitudes[i-1]), math.radians(longitudes[i-1])
        lat2, lon2 = math.radians(latitudes[i]),   math.radians(longitudes[i])
        
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

def calculate_zoom_from_bounds(bounds, map_width=800, map_height=600) -> float:
    """
    Calculate optimal zoom level from bounding box.
    
    :param bounds: geographical bounds of the map
    :param map_width: width of the map
    :param map_height: height of the map
    
    :returns: zoom level
    """
    if len(bounds) != 2: return 10  # Default zoom
    
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

    print(zoom)
    return 13.5
    
    # Clamp to valid Leaflet range (1-19) and round down
    return max(1, min(19, int(zoom)))