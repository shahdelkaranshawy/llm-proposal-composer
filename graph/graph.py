from langgraph.graph import END, StateGraph

from graph.consts import EXTRACT, GENERATE_STRUCTURE, USER_REVIEW_STRUCTURE, GENERATE_SECTION, USER_REVIEW_SECTION, CONCATENATE_SECTIONS, CONTINUE, REORDER_DELETE, EXPORT
from graph.state import GraphState
from graph.nodes.extract import extract_node
from graph.nodes.generate_structure import generate_structure_node
from graph.nodes.user_review_structure import user_review_structure_node
from graph.nodes.generate_section import generate_section_node
from graph.nodes.user_review_section import user_review_section_node
from graph.nodes.concatenate_sections import concatenate_sections_node
from graph.nodes.continue_generation import continue_generation_node
from graph.nodes.reorder_delete import reorder_delete_node
from graph.nodes.export import export_node

def should_continue_to_sections(state: GraphState) -> str:
    """Decide whether to continue to section generation or regenerate structure."""
    if state.get("structure_approved", False):
        return GENERATE_SECTION
    elif state.get("structure_feedback"):
        return GENERATE_STRUCTURE
    else:
        # Stay in review state if neither condition is met
        return USER_REVIEW_STRUCTURE

def should_continue_generating(state: GraphState) -> str:
    """Decide whether to continue generating sections or move to reorder/delete."""
    if state.get("continue_generation", False):
        return GENERATE_SECTION
    else:
        return REORDER_DELETE

def should_regenerate_section(state: GraphState) -> str:
    """Decide whether to regenerate section or move to concatenation."""
    if state.get("section_feedback") and not state.get("section_approved", False):
        return GENERATE_SECTION
    elif state.get("section_approved", False):
        return CONCATENATE_SECTIONS
    else:
        # Stay in review state if neither condition is met
        return USER_REVIEW_SECTION

workflow = StateGraph(GraphState)

# Add all nodes
workflow.add_node(EXTRACT, extract_node)
workflow.add_node(GENERATE_STRUCTURE, generate_structure_node)
workflow.add_node(USER_REVIEW_STRUCTURE, user_review_structure_node)
workflow.add_node(GENERATE_SECTION, generate_section_node)
workflow.add_node(USER_REVIEW_SECTION, user_review_section_node)
workflow.add_node(CONCATENATE_SECTIONS, concatenate_sections_node)
workflow.add_node(CONTINUE, continue_generation_node)
workflow.add_node(REORDER_DELETE, reorder_delete_node)
workflow.add_node(EXPORT, export_node)

# Set entry point
workflow.set_entry_point(EXTRACT)

# Add edges
workflow.add_edge(EXTRACT, GENERATE_STRUCTURE)
workflow.add_edge(GENERATE_STRUCTURE, USER_REVIEW_STRUCTURE)

# Conditional edges for structure review
workflow.add_conditional_edges(
    USER_REVIEW_STRUCTURE,
    should_continue_to_sections,
    {
        GENERATE_STRUCTURE: GENERATE_STRUCTURE,
        GENERATE_SECTION: GENERATE_SECTION,
        USER_REVIEW_STRUCTURE: USER_REVIEW_STRUCTURE,
    },
)

# Section generation flow
workflow.add_edge(GENERATE_SECTION, USER_REVIEW_SECTION)
workflow.add_edge(USER_REVIEW_SECTION, CONCATENATE_SECTIONS)
workflow.add_edge(CONCATENATE_SECTIONS, CONTINUE)

# Conditional edges for section review
workflow.add_conditional_edges(
    USER_REVIEW_SECTION,
    should_regenerate_section,
    {
        GENERATE_SECTION: GENERATE_SECTION,
        CONCATENATE_SECTIONS: CONCATENATE_SECTIONS,
        USER_REVIEW_SECTION: USER_REVIEW_SECTION,
    },
)

# Conditional edges for continuing or finishing
workflow.add_conditional_edges(
    CONTINUE,
    should_continue_generating,
    {
        GENERATE_SECTION: GENERATE_SECTION,
        REORDER_DELETE: REORDER_DELETE,
    },
)

# Final flow
workflow.add_edge(REORDER_DELETE, EXPORT)
workflow.add_edge(EXPORT, END)

# Compile the workflow
app = workflow.compile()

# Generate graph visualization
try:
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
except Exception as e:
    print(f"Could not generate graph visualization: {e}")