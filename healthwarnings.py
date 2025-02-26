import requests

def get_drug_warnings(drug_name):
    """
    (WIP)
    Retrieves drug warnings from the FDA API.
    
    Args:
        drug_name: Name of the drug to search for
        
    Returns:
        dict: Dictionary containing warnings, boxed warnings, and adverse reactions,
              or an error message if the request fails
    """
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        data = response.json()
        
        if "results" in data:
            drug_info = data["results"][0]
            
            warnings = drug_info.get("warnings", ["No warnings available."])[0]
            boxed_warning = drug_info.get("boxed_warning", ["No boxed warning available."])[0]
            adverse_reactions = drug_info.get("adverse_reactions", ["No adverse reactions listed."])[0]
            
            return {
                "warnings": warnings,
                "boxed_warning": boxed_warning,
                "adverse_reactions": adverse_reactions
            }
        else:
            return {"error": "No data found for this drug."}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

# Example usage
if __name__ == "__main__":
    drug_name = "levonorgestrel"
    warnings_data = get_drug_warnings(drug_name)
    
    # Display the results
    print(f"**Warnings for {drug_name}**")
    for key, value in warnings_data.items():
        print(f"{key.capitalize()}: {value}\n")
