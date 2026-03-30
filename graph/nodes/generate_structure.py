from typing import Dict, Any
from graph.state import GraphState
from llm.llm_client import LLMClient

def generate_structure_node(state: GraphState) -> Dict[str, Any]:
    """
    Generate proposal structure using LLM based on RFP and template.
    """
    llm_client = LLMClient()
    
    # Get user instructions if any
    user_instructions = state.get("user_instructions", "")
    
    # Generate structure using LLM
    proposal_outline = llm_client.generate_structure(
        rfp_text=state["rfp_text"],
        template_text=state["template_text"],
        additional_docs=state["additional_docs"],
        user_instructions=user_instructions
    )
    
    return {
        "proposal_outline": proposal_outline,
        "structure_approved": False,
        "structure_feedback": None,
        "current_step": "generate_structure"
    }
