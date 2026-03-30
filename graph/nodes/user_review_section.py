from typing import Dict, Any
from graph.state import GraphState
from llm.llm_client import LLMClient

def user_review_section_node(state: GraphState) -> Dict[str, Any]:
    """
    Handle user review of the generated section.
    If user provides feedback, regenerate section. If approved, move to concatenation.
    """
    # Check if user has provided feedback
    user_feedback = state.get("section_feedback")
    
    if user_feedback and not state.get("section_approved", False):
        # User wants changes - regenerate section
        llm_client = LLMClient()
        
        regenerated_section = llm_client.regenerate_section(
            proposal_outline=state["proposal_outline"],
            concatenated_sections=state.get("concatenated_sections", []),
            current_section=state["current_section"],
            user_feedback=user_feedback
        )
        
        return {
            "current_section": regenerated_section,
            "section_feedback": None,  # Clear feedback after processing
            "section_approved": False,
            "current_step": "review_section"
        }
    
    # If section is approved, move to concatenation
    if state.get("section_approved", False):
        return {
            "current_step": "review_section",
            "section_feedback": None
        }
    
    # Default: wait for user input
    return {
        "current_step": "review_section"
    }
