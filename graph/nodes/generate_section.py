from typing import Dict, Any
from graph.state import GraphState
from llm.llm_client import LLMClient

def generate_section_node(state: GraphState) -> Dict[str, Any]:
    """
    Generate section content using LLM based on proposal outline and previous sections.
    """
    llm_client = LLMClient()
    
    # Determine which section to generate next
    proposal_outline = state["proposal_outline"]
    concatenated_sections = state.get("concatenated_sections", [])
    
    # Get list of all sections from outline
    all_sections = proposal_outline.get("sections", [])
    
    # Get list of already generated section titles
    generated_titles = [s.get("section_title", s.get("title", "")) for s in concatenated_sections]
    
    # Find the next section to generate
    next_section = None
    next_section_title = None
    
    for section in all_sections:
        section_title = section.get("title", section.get("section_title", ""))
        if section_title not in generated_titles:
            next_section = section
            next_section_title = section_title
            break
    
    if not next_section:
        # All sections generated, return empty
        print("⚠️ No more sections to generate")
        return {
            "current_section": None,
            "section_feedback": None,
            "current_step": "generate_section"
        }
    
    print(f"\n📝 Generating section: {next_section_title}")
    print(f"   Progress: {len(generated_titles) + 1}/{len(all_sections)}")
    
    # Get user instructions if any
    user_instructions = state.get("user_instructions", "")
    
    # Generate section content using LLM - pass specific section info
    section_data = llm_client.generate_section(
        proposal_outline=state["proposal_outline"],
        concatenated_sections=concatenated_sections,
        user_instructions=user_instructions,
        rfp_text=state.get("rfp_text", ""),
        template_text=state.get("template_text", ""),
        section_to_generate=next_section_title,
        section_details=next_section
    )
    
    return {
        "current_section": section_data,
        "section_feedback": None,
        "current_step": "generate_section"
    }
