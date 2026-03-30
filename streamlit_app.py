import streamlit as st
import json
import os
import time
from io import BytesIO
from typing import Dict, Any, List
import pandas as pd

# Import our graph and state
from graph.graph import app
from graph.state import GraphState

# Set page config
st.set_page_config(
    page_title="Proposal Composer",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "concatenated_sections": [],  # Initialize empty list for sections
        "current_section": None,
        "section_approved": False,
        "structure_approved": False
    }
if "current_step" not in st.session_state:
    st.session_state.current_step = "upload"

def update_graph_state(updates: Dict[str, Any]):
    """Update the graph state with new values."""
    st.session_state.graph_state.update(updates)

def format_proposal_structure(proposal_outline: Dict[str, Any]) -> str:
    """Format the proposal structure as a table of contents."""
    if not isinstance(proposal_outline, dict):
        return "Invalid proposal structure format"
    
    formatted = ""
    
    # Title
    if "proposal_title" in proposal_outline:
        formatted += f"# {proposal_outline['proposal_title']}\n\n"
    
    # Table of Contents
    sections = proposal_outline.get("sections", [])
    if sections:
        formatted += "## 📋 Table of Contents\n\n"
        for i, section in enumerate(sections, 1):
            if isinstance(section, dict):
                title = section.get("title", f"Section {i}")
                description = section.get("description", "")
                
                # Format as TOC entry
                formatted += f"**{i}. {title}**"
                if description:
                    formatted += f"  \n   *{description}*"
                formatted += "\n\n"
    
    # Overall strategy (if available)
    if "overall_strategy" in proposal_outline:
        formatted += "---\n\n"
        formatted += f"## 🎯 Overall Strategy\n\n{proposal_outline['overall_strategy']}\n\n"
    
    # Strengths to highlight (if available)
    strengths = proposal_outline.get("strengths_to_highlight", [])
    if strengths:
        formatted += "---\n\n"
        formatted += "## 💪 Strengths to Highlight\n\n"
        for strength in strengths:
            formatted += f"• {strength}\n"
        formatted += "\n"
    
    # Potential challenges (if available)
    challenges = proposal_outline.get("potential_challenges", [])
    if challenges:
        formatted += "---\n\n"
        formatted += "## ⚠️ Potential Challenges\n\n"
        for challenge in challenges:
            formatted += f"• {challenge}\n"
        formatted += "\n"
    
    return formatted

def display_table_of_contents(proposal_outline: Dict[str, Any]):
    """Display the proposal structure as an interactive table of contents."""
    
    if not isinstance(proposal_outline, dict):
        st.error("Invalid proposal structure format")
        return
    
    # Handle error case
    if "error" in proposal_outline:
        st.error(f"Error in structure: {proposal_outline.get('error')}")
        return
    
    # Title
    if "proposal_title" in proposal_outline:
        st.markdown(f"## 📋 {proposal_outline['proposal_title']}")
        st.markdown("---")
    
    # Table of Contents - handle different response formats
    sections = proposal_outline.get("sections", [])
    
    # Check if sections are in a different key (like "proposal_template")
    if not sections:
        for key, value in proposal_outline.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                if "section_title" in value[0] or "title" in value[0]:
                    sections = value
                    break
    
    # Special handling: if the entire response is just key-value pairs where values are dicts
    if not sections:
        # Try to extract sections from the structure directly
        potential_sections = []
        for key, value in proposal_outline.items():
            if isinstance(value, dict) and ("section_title" in value or "description" in value):
                # This looks like a section
                section_obj = value.copy()
                if "section_title" not in section_obj and "title" not in section_obj:
                    section_obj["title"] = key
                elif "section_title" in section_obj and "title" not in section_obj:
                    section_obj["title"] = section_obj.pop("section_title")
                potential_sections.append(section_obj)
        
        if potential_sections:
            sections = potential_sections
            st.info("📌 Reconstructed sections from response structure")
    
    if not sections:
        # If still no sections, display whatever structure we have in a readable way
        st.warning("⚠️ No standard sections found. Displaying all content:")
        
        for key, value in proposal_outline.items():
            if key not in ["error", "raw_response"]:
                st.markdown(f"### {key.replace('_', ' ').title()}")
                
                if isinstance(value, list):
                    for i, item in enumerate(value, 1):
                        if isinstance(item, dict):
                            # Display dict items in a nice format
                            title = item.get("section_title", item.get("title", f"Item {i}"))
                            st.markdown(f"**{i}. {title}**")
                            
                            desc = item.get("description", "")
                            if desc:
                                st.markdown(f"> {desc}")
                            
                            subsections = item.get("sub_sections", item.get("subsections", []))
                            if subsections:
                                st.markdown("**Subsections:**")
                                for sub in subsections:
                                    if isinstance(sub, dict):
                                        st.markdown(f"  - {sub.get('section_title', sub.get('title', 'Untitled'))}: {sub.get('description', '')}")
                                    else:
                                        st.markdown(f"  - {sub}")
                            st.markdown("---")
                        else:
                            st.markdown(f"- {item}")
                elif isinstance(value, dict):
                    for k, v in value.items():
                        st.markdown(f"**{k}:** {v}")
                else:
                    st.write(value)
        return
    
    # Display sections in a clean format
    st.markdown("### 📋 Proposal Sections")
    
    for i, section in enumerate(sections, 1):
        if isinstance(section, dict):
            title = section.get("title", section.get("section_title", f"Section {i}"))
            description = section.get("description", "")
            key_points = section.get("key_points", [])
            subsections = section.get("subsections", [])
            rfp_requirements = section.get("rfp_requirements", [])
            
            # Display section header
            st.markdown(f"#### {i}. {title}")
            
            # Description
            if description:
                st.markdown(f"> {description}")
            
            # Subsections
            if subsections:
                st.markdown("**Subsections:**")
                for sub in subsections:
                    st.markdown(f"- {sub}")
            
            # Key points
            if key_points:
                st.markdown("**Key Points:**")
                for point in key_points:
                    st.markdown(f"• {point}")
            
            # RFP requirements
            if rfp_requirements:
                st.markdown("**Addresses RFP Requirements:**")
                for req in rfp_requirements:
                    st.markdown(f"✓ {req}")
            
            st.markdown("---")
    
    # Additional information sections
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall strategy
        if "overall_strategy" in proposal_outline:
            st.markdown("### 🎯 Overall Strategy")
            st.info(proposal_outline['overall_strategy'])
        
        # Strengths
        strengths = proposal_outline.get("strengths_to_highlight", [])
        if strengths:
            st.markdown("### 💪 Strengths to Highlight")
            for strength in strengths:
                st.success(f"✓ {strength}")
    
    with col2:
        # Challenges
        challenges = proposal_outline.get("potential_challenges", [])
        if challenges:
            st.markdown("### ⚠️ Potential Challenges")
            for challenge in challenges:
                st.warning(f"⚠ {challenge}")

def format_section_content(section: Dict[str, Any]) -> str:
    """Format a single section for readable display."""
    if not isinstance(section, dict):
        return "Invalid section format"
    
    formatted = ""
    
    # Title
    title = section.get("section_title", "Untitled Section")
    formatted += f"# {title}\n\n"
    
    # Content
    content = section.get("content", "")
    if content:
        formatted += content + "\n\n"
    
    # Key points if available
    key_points = section.get("key_points", [])
    if key_points:
        formatted += "## Key Points\n"
        for point in key_points:
            formatted += f"- {point}\n"
        formatted += "\n"
    
    return formatted

def run_graph_step(step_name: str):
    """Run a specific step in the graph."""
    try:
        # Get current state
        current_state = st.session_state.graph_state.copy()
        
        # Import the specific node function
        if step_name == "extract":
            from graph.nodes.extract import extract_node
            result = extract_node(current_state)
        elif step_name == "generate_structure":
            from graph.nodes.generate_structure import generate_structure_node
            result = generate_structure_node(current_state)
        elif step_name == "review_structure":
            from graph.nodes.user_review_structure import user_review_structure_node
            result = user_review_structure_node(current_state)
        elif step_name == "generate_section":
            from graph.nodes.generate_section import generate_section_node
            result = generate_section_node(current_state)
        elif step_name == "review_section":
            from graph.nodes.user_review_section import user_review_section_node
            result = user_review_section_node(current_state)
        elif step_name == "concatenate_sections":
            from graph.nodes.concatenate_sections import concatenate_sections_node
            result = concatenate_sections_node(current_state)
        elif step_name == "continue_generation":
            from graph.nodes.continue_generation import continue_generation_node
            result = continue_generation_node(current_state)
        elif step_name == "reorder_delete" or step_name == "reorder_or_delete":
            from graph.nodes.reorder_delete import reorder_delete_node
            result = reorder_delete_node(current_state)
        elif step_name == "export":
            from graph.nodes.export import export_node
            result = export_node(current_state)
        else:
            st.error(f"Unknown step: {step_name}")
            return False
        
        # Update session state with result
        st.session_state.graph_state.update(result)
        st.session_state.current_step = result.get("current_step", step_name)
        
        return True
    except Exception as e:
        st.error(f"Error running graph step: {e}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return False

def upload_page():
    """Page 1: Upload Template and RFP files."""
    st.title("📝 Proposal Composer")
    st.subheader("Upload Documents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload RFP Document")
        rfp_file = st.file_uploader(
            "Choose RFP file",
            type=['pdf', 'docx', 'txt'],
            key="rfp_upload"
        )
    
    with col2:
        st.markdown("### Upload Proposal Template")
        template_file = st.file_uploader(
            "Choose Template file",
            type=['pdf', 'docx', 'txt'],
            key="template_upload"
        )
    
    st.markdown("### Additional Documents (Optional)")
    additional_files = st.file_uploader(
        "Choose additional files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        key="additional_upload"
    )
    
    st.markdown("### User Instructions (Optional)")
    user_instructions = st.text_area(
        "Any specific instructions for the proposal generation:",
        height=100,
        key="user_instructions"
    )
    
    if st.button("Generate Structure", type="primary"):
        if not rfp_file or not template_file:
            st.error("Please upload both RFP and Template files.")
            return
        
        # Show loading indicator with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Prepare files
            status_text.text("📁 Processing uploaded files...")
            progress_bar.progress(20)
            
            rfp_bytes = BytesIO(rfp_file.read())
            template_bytes = BytesIO(template_file.read())
            
            additional_files_data = []
            if additional_files:
                for file in additional_files:
                    file_bytes = BytesIO(file.read())
                    additional_files_data.append({
                        "file": file_bytes,
                        "name": file.name
                    })
            
            # Step 2: Update graph state
            status_text.text("🔄 Updating application state...")
            progress_bar.progress(40)
            
            update_graph_state({
                "rfp_file": rfp_bytes,
                "rfp_name": rfp_file.name,
                "template_file": template_bytes,
                "template_name": template_file.name,
                "additional_files": additional_files_data,
                "user_instructions": user_instructions,
                "current_step": "upload"
            })
            
            # Step 3: Extract text from documents
            status_text.text("📄 Extracting text from documents...")
            progress_bar.progress(60)
            
            if run_graph_step("extract"):
                # Step 4: Generate proposal structure
                status_text.text("🤖 Generating proposal structure with AI...")
                progress_bar.progress(80)
                
                if run_graph_step("generate_structure"):
                    # Step 5: Complete
                    status_text.text("✅ Structure generated successfully!")
                    progress_bar.progress(100)
                    
                    st.session_state.current_step = "structure_generation"
                    st.rerun()
        except Exception as e:
            status_text.text(f"❌ Error: {str(e)}")
            progress_bar.progress(0)
            st.error(f"An error occurred: {str(e)}")

def structure_generation_page():
    """Page 2: Structure Generation and Review."""
    st.title("📋 Proposal Structure")
    
    if "proposal_outline" not in st.session_state.graph_state:
        st.error("No proposal outline found. Please go back to upload page.")
        return
    
    proposal_outline = st.session_state.graph_state["proposal_outline"]
    
    # Display the generated structure
    st.markdown("### Generated Proposal Structure")
    
    if isinstance(proposal_outline, dict) and "error" in proposal_outline:
        st.error(f"Error generating structure: {proposal_outline['error']}")
        st.text_area("Raw LLM Response:", proposal_outline.get("raw_response", ""), height=200)
        return
    
    # Display structure as interactive table of contents
    try:
        display_table_of_contents(proposal_outline)
    except Exception as e:
        st.error(f"Error displaying structure: {e}")
        import traceback
        st.code(traceback.format_exc())
        # Fallback: show sections in a simple way
        st.markdown("### Fallback Display:")
        if "sections" in proposal_outline:
            for i, section in enumerate(proposal_outline["sections"], 1):
                st.markdown(f"**{i}. {section.get('title', 'Untitled')}**")
                st.write(section.get('description', 'No description'))
    
    # User actions
    st.markdown("---")
    st.markdown("### 👉 What would you like to do?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Approve & Continue")
        st.write("Ready to start generating proposal sections?")
        if st.button("✓ Approve Structure", type="primary", use_container_width=True, key="approve_btn"):
            # Update the state BEFORE spinner
            st.session_state.graph_state["structure_approved"] = True
            st.session_state.graph_state["structure_feedback"] = None
            st.session_state.current_step = "section_generation"
            st.rerun()
    
    with col2:
        st.markdown("#### 🔄 Regenerate")
        st.write("Want to make changes to the structure?")
        structure_feedback = st.text_area(
            "Provide feedback for changes:",
            height=80,
            key="structure_feedback_input",
            placeholder="E.g., 'Add a section about sustainability', 'Remove the budget section', etc."
        )
        
        if st.button("🔄 Regenerate Structure", use_container_width=True, key="regen_btn"):
            if structure_feedback.strip():
                # Update the state with feedback
                st.session_state.graph_state["structure_feedback"] = structure_feedback
                st.session_state.graph_state["structure_approved"] = False
                
                # Regenerate the structure
                with st.spinner("🤖 Regenerating structure..."):
                    success = run_graph_step("generate_structure")
                
                if success:
                    st.rerun()
                else:
                    st.error("Failed to regenerate structure. Check errors above.")
            else:
                st.warning("⚠️ Please provide feedback for regeneration.")
    
    # Add expandable section for raw JSON at the bottom (for debugging)
    st.markdown("---")
    with st.expander("🔍 View Raw JSON (for debugging)", expanded=False):
        st.json(proposal_outline)

def section_generation_page():
    """Page 3: Section Generation."""
    st.title("📄 Section Generation")
    
    # Initialize editing mode in session state
    if "editing_section_index" not in st.session_state:
        st.session_state.editing_section_index = None
    
    # Display progress
    concatenated_sections = st.session_state.graph_state.get("concatenated_sections", [])
    current_section = st.session_state.graph_state.get("current_section")
    continue_generation = st.session_state.graph_state.get("continue_generation", True)
    
    # Get proposal outline to know total sections
    proposal_outline = st.session_state.graph_state.get("proposal_outline", {})
    total_sections = len(proposal_outline.get("sections", [])) if isinstance(proposal_outline, dict) else 0
    
    
    # Check if we're done
    all_sections_done = len(concatenated_sections) >= total_sections and total_sections > 0
    
    # If continue_generation is explicitly False OR all sections done, show finalize
    if not current_section and all_sections_done and st.session_state.editing_section_index is None:
        st.success("🎉 All sections completed!")
        if st.button("➡️ Go to Review & Finalize", type="primary", use_container_width=True):
            st.session_state.current_step = "reorder_delete"
            st.rerun()
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Progress")
        st.markdown(f"**Completed: {len(concatenated_sections)} / {total_sections}**")
        
        # Show completed sections with edit buttons
        if concatenated_sections:
            st.markdown("---")
            st.markdown("**📝 Completed Sections:**")
            for i, section in enumerate(concatenated_sections):
                title = section.get("section_title", section.get("title", f"Section {i+1}"))
                
                # Create a container for each section with edit button
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    # Highlight if currently editing
                    if st.session_state.editing_section_index == i:
                        st.info(f"✏️ {title}")
                    else:
                        st.success(f"✅ {title}")
                with col_b:
                    if st.button("✏️", key=f"edit_section_{i}", help=f"Edit {title}"):
                        st.session_state.editing_section_index = i
                        st.rerun()
        
        st.markdown("---")
        
        # Check if we should continue generating
        # Always use simple count logic - more reliable than LLM decision
        should_show_generate_button = len(concatenated_sections) < total_sections
        
        # Button to generate next section if no current section and not editing
        if not current_section and should_show_generate_button and st.session_state.editing_section_index is None:
            if st.button("📝 Generate Next Section", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🤖 Generating section content with AI...")
                    progress_bar.progress(50)
                    
                    if run_graph_step("generate_section"):
                        status_text.text("✅ Section generated successfully!")
                        progress_bar.progress(100)
                        st.rerun()
                except Exception as e:
                    status_text.text(f"❌ Error: {str(e)}")
                    progress_bar.progress(0)
                    st.error(f"An error occurred: {str(e)}")
        elif not current_section and not should_show_generate_button and st.session_state.editing_section_index is None:
            st.success("🎉 All sections generated!")
            if st.button("➡️ Finalize Proposal", type="primary", use_container_width=True):
                st.session_state.current_step = "reorder_delete"
                st.rerun()
        elif st.session_state.editing_section_index is not None:
            st.info("💡 Save or cancel your edits to continue")
        
        # Show info message when there's a current section being reviewed
        if current_section:
            st.info("👉 Review the section on the right and approve or provide feedback")
    
    with col2:
        # Check if we're editing an existing section
        if st.session_state.editing_section_index is not None:
            section_idx = st.session_state.editing_section_index
            if section_idx < len(concatenated_sections):
                editing_section = concatenated_sections[section_idx]
                
                # Display section title
                section_title = editing_section.get("section_title", editing_section.get("title", "Untitled Section"))
                st.markdown(f"### ✏️ Editing: {section_title}")
                st.markdown("---")
                
                # Make content editable
                content = editing_section.get("content", "")
                edited_content = st.text_area(
                    "Section Content",
                    value=content,
                    height=400,
                    key=f"edit_content_{section_idx}",
                    help="Edit the content directly. Markdown formatting is supported."
                )
                
                # User actions
                st.markdown("---")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("💾 Save Changes", type="primary", use_container_width=True, key="save_edit_btn"):
                        # Update the section in concatenated_sections
                        st.session_state.graph_state["concatenated_sections"][section_idx]["content"] = edited_content
                        st.session_state.editing_section_index = None
                        st.success("✅ Changes saved!")
                        st.rerun()
                
                with col_b:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_edit_btn"):
                        st.session_state.editing_section_index = None
                        st.rerun()
                
                # Add expandable section for raw JSON at the bottom (for debugging)
                st.markdown("---")
                with st.expander("🔍 View Raw Section Data (for debugging)", expanded=False):
                    st.json(editing_section)
        
        elif current_section:
            # Display newly generated section for review
            # Display section title
            section_title = current_section.get("section_title", current_section.get("title", "Untitled Section"))
            st.markdown(f"### 📝 {section_title}")
            st.markdown("---")
            
            # Display section content - NOT as JSON!
            content = current_section.get("content", "")
            if content:
                # Display the actual content
                st.markdown(content)
            else:
                st.warning("No content found in this section")
            
            # Display key points if available
            key_points = current_section.get("key_points", [])
            if key_points:
                st.markdown("### Key Points")
                for point in key_points:
                    st.markdown(f"• {point}")
            
            # User actions
            st.markdown("---")
            st.markdown("### 👉 What would you like to do?")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### ✅ Approve Section")
                if st.button("✓ Approve & Continue", type="primary", use_container_width=True, key="approve_section_btn"):
                    st.session_state.graph_state["section_approved"] = True
                    st.session_state.graph_state["section_feedback"] = None
                    
                    with st.spinner("🔄 Processing section..."):
                        # Run the workflow steps
                        run_graph_step("review_section")
                        run_graph_step("concatenate_sections")
                        run_graph_step("continue_generation")
                        
                        # Rerun to show next section button
                        st.rerun()
            
            with col_b:
                st.markdown("#### 🔄 Regenerate Section")
                section_feedback = st.text_area(
                    "Provide feedback:",
                    height=80,
                    key="section_feedback_input",
                    placeholder="E.g., 'Make it more concise', 'Add more technical details', etc."
                )
                
                if st.button("🔄 Regenerate", use_container_width=True, key="regen_section_btn"):
                    if section_feedback.strip():
                        st.session_state.graph_state["section_feedback"] = section_feedback
                        st.session_state.graph_state["section_approved"] = False
                        
                        with st.spinner("🤖 Regenerating section..."):
                            if run_graph_step("review_section"):
                                st.rerun()
                    else:
                        st.warning("⚠️ Please provide feedback for regeneration.")
            
            # Add expandable section for raw JSON at the bottom (for debugging)
            st.markdown("---")
            with st.expander("🔍 View Raw Section Data (for debugging)", expanded=False):
                st.json(current_section)
        else:
            st.info("Click 'Generate Next Section' to start generating sections, or click the ✏️ button next to a completed section to edit it.")

def review_proposal_page():
    """Page 4: Review and Reorder Proposal."""
    st.title("🔍 Review & Finalize Proposal")
    
    concatenated_sections = st.session_state.graph_state.get("concatenated_sections", [])
    
    if not concatenated_sections:
        st.error("No sections to review. Please generate sections first.")
        return
    
    st.markdown(f"### ✅ Your Proposal ({len(concatenated_sections)} Sections)")
    st.info("💡 **Tip:** Check the 'Delete' checkbox to remove a section, then click 'Apply Changes'")
    
    # Create a dataframe for easy reordering and deletion
    sections_data = []
    for i, section in enumerate(concatenated_sections):
        # Handle both "section_title" and "title" keys
        title = section.get("section_title", section.get("title", f"Section {i+1}"))
        content = section.get("content", "")
        preview = content[:150] + "..." if len(content) > 150 else content if content else "No content"
        
        sections_data.append({
            "#": i + 1,
            "Section Title": title,
            "Preview": preview,
            "❌ Delete": False
        })
    
    df = pd.DataFrame(sections_data)
    
    # Allow editing with data editor
    st.markdown("#### 📝 Edit Sections")
    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "#": st.column_config.NumberColumn(
                "#",
                help="Section number",
                disabled=True,
                width="small"
            ),
            "Section Title": st.column_config.TextColumn(
                "Section Title",
                help="Title of the section",
                disabled=True,
                width="medium"
            ),
            "Preview": st.column_config.TextColumn(
                "Preview",
                help="First 150 characters of content",
                disabled=True,
                width="large"
            ),
            "❌ Delete": st.column_config.CheckboxColumn(
                "❌ Delete",
                help="Check to delete this section",
                default=False,
                width="small"
            )
        },
        key="sections_editor"
    )
    
    # Show which sections will be deleted
    sections_to_delete_indices = []
    for idx, row in edited_df.iterrows():
        if row["❌ Delete"]:
            sections_to_delete_indices.append(idx)
    
    if sections_to_delete_indices:
        st.warning(f"⚠️ {len(sections_to_delete_indices)} section(s) marked for deletion")
        for idx in sections_to_delete_indices:
            title = edited_df.iloc[idx]["Section Title"]
            st.write(f"  - ❌ {title}")
    
    # Apply changes button
    col1, col2 = st.columns(2)
    
    with col1:
        if sections_to_delete_indices:
            if st.button("🗑️ Apply Deletions", type="secondary", use_container_width=True):
                update_graph_state({"sections_to_delete": sections_to_delete_indices})
                if run_graph_step("reorder_delete"):
                    st.success(f"✅ Deleted {len(sections_to_delete_indices)} section(s)")
                    time.sleep(0.5)
                    st.rerun()
    
    with col2:
        # Skip directly to export without changes
        if st.button("➡️ Continue to Export", type="primary", use_container_width=True):
            st.session_state.current_step = "export"
            st.rerun()
    
    # Preview sections with reordering
    st.markdown("---")
    st.markdown("### 📄 Section Previews & Reordering")
    st.write("Use the arrows or drag to reorder sections:")
    
    # Create reorderable sections using columns
    for i, section in enumerate(concatenated_sections):
        # Handle both "section_title" and "title" keys
        title = section.get("section_title", section.get("title", f"Section {i+1}"))
        content = section.get("content", "No content available")
        
        # Section container with controls
        col_num, col_title, col_up, col_down = st.columns([1, 6, 1, 1])
        
        with col_num:
            st.write(f"**{i+1}.**")
        
        with col_title:
            with st.expander(f"{title}", expanded=False):
                st.markdown(content)
        
        with col_up:
            if i > 0:  # Not the first item
                if st.button("⬆️", key=f"up_{i}", help="Move up"):
                    # Swap with previous
                    concatenated_sections[i], concatenated_sections[i-1] = concatenated_sections[i-1], concatenated_sections[i]
                    st.session_state.graph_state["concatenated_sections"] = concatenated_sections
                    st.rerun()
        
        with col_down:
            if i < len(concatenated_sections) - 1:  # Not the last item
                if st.button("⬇️", key=f"down_{i}", help="Move down"):
                    # Swap with next
                    concatenated_sections[i], concatenated_sections[i+1] = concatenated_sections[i+1], concatenated_sections[i]
                    st.session_state.graph_state["concatenated_sections"] = concatenated_sections
                    st.rerun()
    
    # Note: Deletions are handled by the button above
    # Export button is in the columns above

def export_page():
    """Page 5: Export Final Proposal."""
    st.title("📤 Export Proposal")
    
    concatenated_sections = st.session_state.graph_state.get("concatenated_sections", [])
    exported_document = st.session_state.graph_state.get("exported_document")
    
    if not concatenated_sections:
        st.error("No sections to export.")
        return
    
    # Display final proposal
    st.markdown("### Final Proposal Preview")
    
    for i, section in enumerate(concatenated_sections):
        # Handle both "section_title" and "title" keys
        title = section.get("section_title", section.get("title", f"Section {i+1}"))
        content = section.get("content", "No content available")
        
        st.markdown(f"## {i+1}. {title}")
        st.markdown(content)
        st.markdown("---")
    
    # Export functionality
    if st.button("Export as Word Document", type="primary"):
        with st.spinner("🔄 Generating Word document..."):
            if not exported_document:
                # Run export step
                if run_graph_step("export"):
                    exported_document = st.session_state.graph_state.get("exported_document")
            
            if exported_document:
                st.download_button(
                    label="Download Proposal",
                    data=exported_document.getvalue(),
                    file_name="proposal.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("Failed to generate document.")

def main():
    """Main application logic."""
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Determine current step
    current_step = st.session_state.current_step
    
    if current_step == "upload":
        page = "Upload Documents"
    elif current_step in ["structure_generation", "review_structure"]:
        page = "Structure Review"
    elif current_step in ["section_generation", "generate_section", "review_section", "concatenate_sections", "continue"]:
        page = "Section Generation"
    elif current_step in ["reorder_or_delete", "reorder_delete"]:
        page = "Review Proposal"
    elif current_step == "export":
        page = "Export"
    else:
        page = "Upload Documents"
        current_step = "upload"
    
    st.sidebar.markdown(f"**Current Page:** {page}")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home"):
        st.session_state.current_step = "upload"
        st.rerun()
    
    # Display current page
    if current_step == "upload":
        upload_page()
    elif current_step in ["structure_generation", "review_structure"]:
        structure_generation_page()
    elif current_step in ["section_generation", "generate_section", "review_section", "concatenate_sections", "continue"]:
        section_generation_page()
    elif current_step in ["reorder_or_delete", "reorder_delete"]:
        review_proposal_page()
    elif current_step == "export":
        export_page()

if __name__ == "__main__":
    main()
