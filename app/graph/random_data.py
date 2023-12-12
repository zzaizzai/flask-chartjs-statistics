from typing import Tuple, Dict, Any, List


    
def get_minY_maxY(data:List[Dict[str, Any]], headers:List[str]) -> Tuple[float, float]:
    result = []
    
    if len(data) <= 0:
        return 0, 0
    
    # Iterate through each dictionary in the data
    for entry in data:
        for key in headers:
            # Check if the key is present and not None
            if key in entry and entry[key] is not None:
                # Assuming the key contains numeric data
                result.append(float(entry[key]))

    # Calculate min and max values
    min_value = min(result)
    max_value = max(result)

    return min_value, max_value


