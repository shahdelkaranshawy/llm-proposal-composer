from typing import Dict, Any
from graph.state import GraphState

def concatenate_sections_node(state: GraphState) -> Dict[str, Any]:
    """
    Concatenate the approved section to the list of generated sections.
    """
    # Get current concatenated sections
    concatenated_sections = state.get("concatenated_sections", [])
    
    # Get the current approved section
    current_section = state.get("current_section")
    
    if current_section:
        # Add the approved section to the concatenated list
        concatenated_sections.append(current_section)
    
    return {
        "concatenated_sections": concatenated_sections,
        "current_section": None,  # Clear current section after concatenation
        "section_approved": False,  # Reset approval flag
        "current_step": "concatenate_sections"
    }
