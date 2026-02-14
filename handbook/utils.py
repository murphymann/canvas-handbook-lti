import json
import os
from django.conf import settings


def load_handbook_json(course_code):
    """
    Load handbook JSON data for a given course code.
    
    Args:
        course_code: The unit code (e.g., 'EDET100')
        
    Returns:
        Dictionary containing the parsed JSON data, or None if not found
    """
    # Build the path to the JSON file
    json_filename = f"{course_code}.json"
    json_path = os.path.join('handbook', 'data', json_filename)
    
    # DEBUG: Print what we're looking for
    print(f"Looking for file: {json_path}")
    print(f"File exists: {os.path.exists(json_path)}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if file exists
    if not os.path.exists(json_path):
        print(f"File not found at: {json_path}")
        return None
    
    # Load and return the JSON data
    print(f"Attempting to open file: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            print("File opened successfully, parsing JSON...")
            data = json.load(f)
            print(f"JSON parsed successfully! Type: {type(data)}")
            print(f"JSON has {len(data)} keys")
            return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in {json_filename}: {e}")
        return None
    except Exception as e:
        print(f"Error loading {json_filename}: {e}")
        print(f"Error type: {type(e)}")
        return None


def parse_handbook_data(json_data):
    """
    Extract key information from the handbook JSON structure.
    
    Args:
        json_data: The raw JSON data from Sitecore
        
    Returns:
        Dictionary with extracted and organized handbook information
    """
    if not json_data:
        print("ERROR: json_data is None or empty")
        return None
    
    # DEBUG: Print what we received
    print(f"Parsing JSON data. Keys: {list(json_data.keys())}")
    
    # Extract basic unit information
    unit_code = json_data.get('code', '')
    unit_name = json_data.get('name', '')
    credit_points = json_data.get('unitsMaximum', 0)
    year = json_data.get('yearApplied', '')
    
    print(f"Extracted: {unit_code} - {unit_name} ({credit_points} points) - Year: {year}")

    # Extract from the payload components
    components = json_data.get('payload', {}).get('components', [])
    print(f"Found {len(components)} components")
    
    # Helper function to find component by identifier
    def find_component(identifier):
        for component in components:
            if component.get('componentIntegrationIdentifier') == identifier:
                return component.get('payload', {}).get('value')
        return None
    
    # Extract key fields
    unit_description = find_component('unit_desc')
    prerequisites = find_component('handbook_prereq')
    unit_content = find_component('unit_content')
    teaching_org = find_component('teaching_org')
    learning_strategy = find_component('learning_strategy')
    assessment_strategy = find_component('assessment_strategy')
    references = find_component('text_and_references')
    
    # Extract complex structured data
    learning_outcomes = extract_learning_outcomes(components)
    graduate_capabilities = extract_graduate_capabilities(components)
    assessments = extract_assessments(components)
    
    print(f"Found {len(learning_outcomes)} learning outcomes")
    print(f"Found {len(graduate_capabilities)} graduate capabilities")
    print(f"Found {len(assessments)} assessments")
    
    result = {
        'code': unit_code,
        'name': unit_name,
        'credit_points': credit_points,
        'year': year,
        'description': unit_description,
        'prerequisites': prerequisites,
        'teaching_org': teaching_org,
        'content': unit_content,
        'learning_strategy': learning_strategy,
        'assessment_strategy': assessment_strategy,
        'references': references,
        'learning_outcomes': learning_outcomes,
        'graduate_capabilities': graduate_capabilities,
        'assessments': assessments,
    }
    
    print(f"Returning parsed data for: {result.get('code')}")
    
    return result


def extract_learning_outcomes(components):
    """
    Extract learning outcomes from the components array.
    
    Args:
        components: List of component dictionaries
        
    Returns:
        List of learning outcome dictionaries
    """
    for component in components:
        if component.get('componentIntegrationIdentifier') == 'learning_outcomes_v2':
            rows = component.get('payload', {}).get('rows', [])
            outcomes = []
            
            for row in rows:
                cells = row.get('cells', [])
                if len(cells) >= 2:
                    outcome = {
                        'number': cells[0].get('value', ''),
                        'description': cells[1].get('value', ''),
                    }
                    outcomes.append(outcome)
            
            return outcomes
    
    return []


def extract_graduate_capabilities(components):
    """
    Extract graduate capabilities from the components array.
    
    Args:
        components: List of component dictionaries
        
    Returns:
        List of graduate capability dictionaries
    """
    for component in components:
        if component.get('componentIntegrationIdentifier') == 'graduate_capabillities_v2':
            rows = component.get('payload', {}).get('rows', [])
            capabilities = []
            
            for row in rows:
                cells = row.get('cells', [])
                if len(cells) >= 3:
                    capability = {
                        'id': cells[0].get('value', ''),
                        'name': cells[1].get('value', ''),
                        'description': cells[2].get('value', ''),
                    }
                    capabilities.append(capability)
            
            return capabilities
    
    return []

def extract_assessments(components):
    """
    Extract assessment tasks from the components array.
    Handles different table structures by using column metadata.
    
    Args:
        components: List of component dictionaries
        
    Returns:
        List of assessment task dictionaries
    """
    for component in components:
        if component.get('componentIntegrationIdentifier') == 'assessment_overview_v2':
            payload = component.get('payload', {})
            columns = payload.get('columns', [])
            rows = payload.get('rows', [])
            
            # Find which columns contain description and weighting
            description_col_idx = None
            weighting_col_idx = None
            
            for idx, col in enumerate(columns):
                heading = col.get('heading', '').lower()
                # Look for description column
                if 'description' in heading or 'kind and purpose' in heading:
                    description_col_idx = idx
                # Look for weighting column
                if 'weighting' in heading:
                    weighting_col_idx = idx
            
            print(f"DEBUG: Found description at column {description_col_idx}, weighting at column {weighting_col_idx}")
            
            assessments = []
            
            for row in rows:
                cells = row.get('cells', [])
                
                # Extract data based on column positions we found
                description = ''
                weighting = ''
                
                if description_col_idx is not None and description_col_idx < len(cells):
                    description = cells[description_col_idx].get('value', '')
                
                if weighting_col_idx is not None and weighting_col_idx < len(cells):
                    weighting = cells[weighting_col_idx].get('value', '')
                
                # Only add if we have at least a description
                if description:
                    assessment = {
                        'description': description,
                        'weighting': weighting,
                    }
                    assessments.append(assessment)
            
            print(f"DEBUG: Extracted {len(assessments)} assessments")
            return assessments
    
    return []