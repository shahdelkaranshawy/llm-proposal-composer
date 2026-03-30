from typing import Dict, Any, List
from graph.state import GraphState

def reorder_delete_node(state: GraphState) -> Dict[str, Any]:
    """
    Handle reordering and deletion of sections based on user input.
    """
    # Get current concatenated sections
    concatenated_sections = state.get("concatenated_sections", [])
    
    # Get user actions for reordering/deletion
    sections_to_delete = state.get("sections_to_delete", [])
    new_order = state.get("new_section_order")
    
    # Delete specified sections
    if sections_to_delete:
        # Convert to set for faster lookup
        delete_indices = set(sections_to_delete)
        # Keep sections that are not marked for deletion
        concatenated_sections = [
            section for i, section in enumerate(concatenated_sections)
            if i not in delete_indices
        ]
    
    # Reorder sections if new order is provided
    if new_order and len(new_order) == len(concatenated_sections):
        # Reorder sections according to new order
        concatenated_sections = [
            concatenated_sections[i] for i in new_order
        ]
    
    return {
        "concatenated_sections": concatenated_sections,
        "sections_to_delete": [],  # Clear deletion list
        "new_section_order": None,  # Clear reorder list
        "current_step": "reorder_or_delete"
    }
