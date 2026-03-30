from typing import Dict, Any
from graph.state import GraphState
from llm.llm_client import LLMClient

def continue_generation_node(state: GraphState) -> Dict[str, Any]:
    """
    Decide whether to continue generating sections or finish.
    """
    llm_client = LLMClient()
    
    # Get current state info
    proposal_outline = state["proposal_outline"]
    concatenated_sections = state.get("concatenated_sections", [])
    
    # Use LLM to decide whether to continue
    should_continue = llm_client.decide_continue(
        proposal_outline=proposal_outline,
        concatenated_sections=concatenated_sections
    )
    
    return {
        "continue_generation": should_continue,
        "current_step": "continue"
    }
