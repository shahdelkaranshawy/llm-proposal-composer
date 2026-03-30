from typing import Dict, Any
from graph.state import GraphState
from functions.extract_text import load_and_extract_documents

def extract_node(state: GraphState) -> Dict[str, Any]:
    """
    Extract text from uploaded RFP, Template, and additional documents.
    This node processes the uploaded files and extracts their text content.
    """
    # Get uploaded files from state (these will be set by Streamlit UI)
    rfp_file = state.get("rfp_file")
    rfp_name = state.get("rfp_name")
    template_file = state.get("template_file")
    template_name = state.get("template_name")
    additional_files = state.get("additional_files", [])
    
    # Extract text from all documents
    extracted_data = load_and_extract_documents(
        rfp_file=rfp_file,
        rfp_name=rfp_name,
        template_file=template_file,
        template_name=template_name,
        additional_files=additional_files
    )
    
    return {
        "rfp_text": extracted_data["rfp_text"],
        "template_text": extracted_data["template_text"],
        "additional_docs": extracted_data["additional_docs"],
        "current_step": "extract"
    }
