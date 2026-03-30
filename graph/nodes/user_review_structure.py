from typing import Dict, Any
from graph.state import GraphState
from llm.llm_client import LLMClient

def user_review_structure_node(state: GraphState) -> Dict[str, Any]:
    """
    Handle user review of the proposal structure.
    If user provides feedback, regenerate structure. If approved, move to section generation.
    """
    # Check if user has provided feedback
    user_feedback = state.get("structure_feedback")
    
    if user_feedback and not state.get("structure_approved", False):
        # User wants changes - regenerate structure
        llm_client = LLMClient()
        
        regenerated_outline = llm_client.regenerate_structure(
            rfp_text=state["rfp_text"],
            template_text=state["template_text"],
            proposal_outline=state["proposal_outline"],
            user_feedback=user_feedback
        )
        
        return {
            "proposal_outline": regenerated_outline,
            "structure_feedback": None,  # Clear feedback after processing
            "structure_approved": False,
            "current_step": "review_structure"
        }
    
    # If structure is approved, move to section generation
    if state.get("structure_approved", False):
        return {
            "current_step": "review_structure",
            "structure_feedback": None
        }
    
    # Default: wait for user input
    return {
        "current_step": "review_structure"
    }
