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