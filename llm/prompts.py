"""
Prompt templates for the Proposal Composer LLM interactions.
"""

from typing import Any, Dict, Optional, List


def generate_structure_prompt(
    rfp_text: str,
    proposal_template: str,
    additional_docs: Optional[List[Dict[str, Any]]] = None,
    user_instructions: Optional[str] = None,
) -> str:
    """
    Generate a comprehensive prompt for creating proposal structure based on RFP and template.
    """
    
    # Format additional documents
    additional_docs_text = ""
    if additional_docs:
        for doc in additional_docs:
            additional_docs_text += f"\nDocument: {doc.get('filename', 'Unknown')}\n{doc.get('text', '')}\n"
    
    # Format user instructions
    user_instructions_text = user_instructions or ""
    
    prompt = f"""You are an assistant that generates proposal outlines.

Given this RFP text:
{rfp_text}

And this proposal template:
{proposal_template}

And any additional documents:
{additional_docs_text}

And the user instructions:
{user_instructions_text}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ANALYZE THE TEMPLATE DOCUMENT - Examine the template carefully to identify which sections have pre-written content (actual text, not just headings or placeholders)
2. COPY PRE-WRITTEN CONTENT - If a section in the template has actual written content (paragraphs, tables, images, forms, etc.), that section should be marked to use the template content AS-IS
3. PRESERVE ALL TEMPLATE ELEMENTS - Keep headers, footers, page numbers, logos, formatting, fonts, colors, spacing, and any other visual elements exactly as shown in the template
4. IDENTIFY CONTENT SECTIONS - Mark sections that only have placeholders or headings as needing new content generation
5. MAINTAIN EXACT STRUCTURE - Use the same section order, numbering system (1.1, 1.2 or A, B, C, etc.), and hierarchy as the template
6. TEMPLATE FORMATTING RULES - The final proposal must LOOK EXACTLY like the template with only the content sections updated

Generate a structured outline in valid JSON format. Return ONLY a JSON object with this exact structure:

{{
    "proposal_title": "Title of the proposal",
    "sections": [
        {{
            "title": "Exact section title from template (e.g., 'Prepared for', 'Copyright', 'HYVE Overview', etc.)",
            "description": "What this section should cover based on RFP requirements",
            "subsections": ["Subsection 1 from template", "Subsection 2 from template"],
            "key_points": ["Key point 1", "Key point 2"],
            "use_template_content": true/false,
            "formatting_notes": "Any special formatting from template (page breaks, headers, etc.)"
        }}
    ]
}}

CRITICAL NOTE ON use_template_content FLAG - BE CONSISTENT:

Set to TRUE for these sections (they have pre-written content or tables in template):
* Administrative sections: Copyright, Document Information, Document Change Record, Document Reviewers, Prepared for, Table of Contents
* Company information: HYVE Overview, Who We Are, What We Do
* ANY section that has actual content, tables, charts, or images in the template
* ANY section where you see real text (not "[To be completed]" or similar placeholders)

Set to FALSE ONLY for sections that are:
* Completely empty in the template
* Have placeholder text like "[To be completed]", "[Insert content here]", "[TBD]"
* Are meant to be customized for each proposal (Executive Summary, Project Approach, etc.)

CONSISTENCY RULE: Always mark the SAME sections the same way every time. For example:
- "Copyright" → ALWAYS true
- "HYVE Overview" → ALWAYS true (if pre-written in template)
- "Executive Summary" → ALWAYS false (needs RFP-specific content)
- "Timeline" → Check template: if it has a pre-filled timeline table → true, if empty/placeholder → false

The goal is to preserve the template EXACTLY and only generate new content where the template has placeholders.

IMPORTANT: 
- Return ONLY valid JSON
- The "sections" key must be an array of section objects
- Each section must have at least "title" and "description"
- Preserve ALL sections from the template, including administrative sections
- Do not include any text outside the JSON object
"""

    return prompt


def regenerate_structure_prompt(
    rfp_text: str,
    proposal_template: str,
    current_structure: Dict[str, Any],
    user_feedback: str,
    additional_docs: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generate a prompt for regenerating proposal structure based on user feedback.
    """
    
    prompt = f"""You are an assistant that revises proposal outlines. Revise the outline according to user feedback. If feedback applies only to certain parts of the outline, leave the rest unchanged.

Given this RFP text:
{rfp_text}

And this template structure:
{proposal_template}

And this proposal outline you created:
{current_structure}

And user feedback on outline:
{user_feedback}

CRITICAL INSTRUCTIONS WHEN REVISING:
1. MAINTAIN TEMPLATE COMPLIANCE - Keep the template's structure, formatting, and section organization
2. PRESERVE TEMPLATE SECTIONS - Do not remove administrative or formatting sections from the template (cover pages, copyright, document info, etc.)
3. INCORPORATE FEEDBACK - Apply the user's feedback while staying true to the template format
4. KEEP TEMPLATE FORMATTING - Maintain any numbering, styling, or organizational elements from the template

Generate a revised structured outline in valid JSON format. Return ONLY a JSON object with this exact structure:

{{
    "proposal_title": "Title of the proposal",
    "sections": [
        {{
            "title": "Exact section title from template",
            "description": "What this section should cover based on RFP requirements",
            "subsections": ["Subsection 1 from template", "Subsection 2 from template"],
            "key_points": ["Key point 1", "Key point 2"],
            "formatting_notes": "Any special formatting from template"
        }}
    ]
}}

IMPORTANT: 
- Return ONLY valid JSON
- The "sections" key must be an array of section objects
- Each section must have at least "title" and "description"
- Preserve the template's structure and formatting requirements
- Do not include any text outside the JSON object
"""

    return prompt


def generate_section_prompt(
    proposal_outline: Dict[str, Any],
    section_title: str,
    concatenated_sections: List[Dict[str, Any]],
    rfp_text: str,
    template_text: str,
    additional_docs: Optional[List[Dict[str, Any]]] = None,
    user_instructions: Optional[str] = None,
) -> str:
    """
    Generate a prompt for writing a specific proposal section.
    """
    
    # Format previously generated sections
    concatenated_sections_text = ""
    if concatenated_sections:
        for section in concatenated_sections:
            concatenated_sections_text += f"\nSection: {section.get('section_title', 'Unknown Title')}\n{section.get('content', '')}\n"
    
    # Format user instructions
    user_instructions_text = user_instructions or ""
    
    prompt = f"""You are an assistant that generates section content for each section in the proposal.

Given this proposal outline:
{proposal_outline}

And the TEMPLATE DOCUMENT with pre-written content:
{template_text}

And previously generated sections:
{concatenated_sections_text}

And the user instructions:
{user_instructions_text}

CRITICAL FORMATTING INSTRUCTIONS:
1. USE PRE-WRITTEN TEMPLATE CONTENT - If the section is marked with "use_template_content": true in the outline, COPY the exact text from the template for this section. Do NOT generate new content. Extract and use the pre-written content from the template AS-IS.
2. MATCH THE TEMPLATE FORMAT - For sections requiring new content, follow the template's formatting (page headers, footers, numbering styles, fonts)
3. PRESERVE TEMPLATE STRUCTURE - Follow the exact section organization and hierarchy from the template
4. MAINTAIN CONSISTENCY - Use the same tone, style, and formatting conventions as indicated in the template
5. INCLUDE TEMPLATE ELEMENTS - For administrative sections, extract the exact text from the template
6. FOLLOW NUMBERING/STYLING - Match any numbering schemes (1.1, 1.2 or I, II, III, etc.) shown in the template

YOUR TASK FOR THIS SECTION:

Check the proposal outline for this section's "use_template_content" flag:

IF "use_template_content" is TRUE:
- Go to the template document text provided above
- Find this exact section in the template
- Copy ALL the TEXT content from that section VERBATIM (word-for-word, exactly as written)
- For images: Include a description like "[IMAGE: Company logo]" or "[IMAGE: Chart showing XYZ]"
- **For tables in template: Copy them using the [TABLE] format:**
  [TABLE]
  | Header1 | Header2 | Header3 |
  |---------|---------|---------|
  | Cell1   | Cell2   | Cell3   |
  [/TABLE]
- Include any formatting notes like "[PAGE BREAK]", "[HEADER: text]", "[FOOTER: text]"
- DO NOT generate new content, DO NOT modify the template text - copy it exactly including any tables

IF "use_template_content" is FALSE (or not specified):
- Generate NEW professional, HIGHLY DETAILED and ELABORATE proposal content for this section
- Base content on the RFP requirements and proposal outline
- Write COMPREHENSIVE content (MINIMUM 1200-2000 words - be thorough and detailed!)
- Include MULTIPLE SUBSECTIONS with headings (use ## for main subsections, ### for sub-subsections)
- Aim for AT LEAST 3-5 major subsections per section
- **INCLUDE TABLES** where data is best presented in tabular format using this EXACT format:

[TABLE]
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
[/TABLE]

Use tables for these types of content:
* **Project Timeline/Schedule** - Phase | Duration | Start Date | End Date | Key Deliverables
* **Budget/Cost Breakdown** - Item | Description | Quantity | Unit Cost | Total Cost
* **Team Structure** - Role | Name | Years of Experience | Key Responsibilities
* **Technical Specifications** - Component | Technology | Version | Purpose
* **Milestones** - Milestone Name | Target Date | Success Criteria | Dependencies
* **Deliverables List** - Deliverable | Description | Format | Delivery Date
* **Risk Assessment** - Risk | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation Strategy
* **Resource Allocation** - Resource | Allocation % | Duration | Cost
* **Comparison Tables** - Feature | Our Approach | Alternative | Advantage

IMPORTANT: Always use tables when presenting structured data - they make proposals more professional and easier to read!

- Follow the template's writing style and tone
- Write complete, detailed paragraphs with:
  * Specific examples and case studies
  * Technical details and methodologies
  * Data, metrics, and quantifiable information
  * Benefits and value propositions
  * Risk mitigation strategies where relevant
- Break down complex topics into logical subsections
- Use clear, professional business language

Generate section content in valid JSON format. Return ONLY a JSON object with this EXACT structure:

{{
    "section_title": "Title of the section",
    "content": "The actual section content goes here - either copied from template or newly generated.

FOR NEW CONTENT - Example format with subsections:

Our approach to this project encompasses three key areas that ensure successful delivery and long-term value.

## 1. Discovery and Planning Phase

We begin with a comprehensive discovery process that includes stakeholder interviews, requirements gathering, and technical assessment. This phase typically spans 2-3 weeks and involves...

### 1.1 Stakeholder Engagement
Our team conducts detailed interviews with key stakeholders to understand business objectives, user needs, and technical constraints. We use structured interview techniques...

### 1.2 Requirements Documentation
Following stakeholder engagement, we create detailed requirements documentation including functional specifications, technical requirements, and success criteria...

## 2. Implementation Strategy

Our implementation follows an agile methodology with 2-week sprints...

[Continue with detailed, comprehensive content organized into logical subsections]

NOTE: Use ## for main subsections, ### for sub-subsections. Write 800-1500 words with specific details."
}}

CRITICAL REQUIREMENTS FOR CONTENT:
- "content" must contain the ACTUAL TEXT (not instructions, not descriptions)
- For template sections: Extract and copy the real text from the template document
- For NEW sections: Write COMPREHENSIVE, ELABORATE, DETAILED content with:
  * MINIMUM 800-1500 words (longer is better for important sections)
  * Multiple subsections (use ## and ### headings to organize)
  * Specific examples, case studies, and real-world applications
  * Technical details and methodologies explained thoroughly
  * Data points, metrics, timelines, and quantifiable information
  * Benefits, value propositions, and competitive advantages
  * Risk analysis and mitigation strategies
  * Implementation details and step-by-step approaches
- Write in professional, persuasive business language
- Use subsections to organize complex topics logically
- Include transitions between subsections for smooth flow
- Do NOT use bullet points for main content - write full prose paragraphs
- Follow any formatting conventions from the template
- Return ONLY valid JSON

If {user_instructions_text} is empty, proceed to generate the section content without them.
"""

    return prompt


def regenerate_section_prompt(
    proposal_outline: Dict[str, Any],
    current_section: Dict[str, Any],
    user_feedback: str,
    concatenated_sections: List[Dict[str, Any]],
    rfp_text: str,
    template_text: str,
    additional_docs: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generate a prompt for regenerating a proposal section based on user feedback.
    """
    
    # Format previously generated sections
    concatenated_sections_text = ""
    if concatenated_sections:
        for section in concatenated_sections:
            concatenated_sections_text += f"\nSection: {section.get('section_title', 'Unknown Title')}\n{section.get('content', '')}\n"
    
    prompt = f"""You are an assistant that revises section content for each section in the proposal. Revise the section according to user feedback. If feedback applies only to certain parts of the section, leave the rest unchanged.

Given this proposal outline:
{proposal_outline}

And previously generated sections:
{concatenated_sections_text}

And the last section generated:
{current_section}

And user feedback on the last section generated:
{user_feedback}

CRITICAL FORMATTING INSTRUCTIONS:
1. MAINTAIN TEMPLATE FORMAT - Keep the same formatting style, headers, and structure as indicated in the proposal outline
2. PRESERVE FORMATTING ELEMENTS - If the template specifies headers, footers, page breaks, or special formatting, maintain those
3. FOLLOW TEMPLATE STYLE - Match the tone, language style, and formatting conventions from the template
4. INCORPORATE FEEDBACK - Apply the user's feedback while maintaining the template's format and style

Generate revised section content in valid JSON format. Return ONLY a JSON object with this exact structure:

{{
    "section_title": "Name of the section (exact title from template)",
    "content": "Full written content of the section in professional business proposal format that follows the template's formatting style. This should be several paragraphs of actual proposal text that incorporates the user feedback while maintaining template formatting."
}}

IMPORTANT:
- The "content" field must contain the ACTUAL written section content (multiple paragraphs)
- Incorporate the user feedback into the content
- Write in professional business language matching the template's style
- Maintain any formatting requirements from the template
- For administrative sections (Copyright, Document Info), use appropriate template-style content
- Return ONLY valid JSON"""

    return prompt


def continue_or_finish_prompt(
    proposal_outline: Dict[str, Any],
    concatenated_sections: List[Dict[str, Any]],
    rfp_text: str,
    template_text: str,
) -> str:
    """
    Generate a prompt to determine whether to continue generating sections or finish the proposal.
    """
    
    # Format previously generated sections
    concatenated_sections_text = ""
    if concatenated_sections:
        for section in concatenated_sections:
            concatenated_sections_text += f"\nSection: {section.get('section_title', 'Unknown Title')}\n{section.get('content', '')}\n"
    
    # Extract section info for clearer comparison
    outline_sections = []
    if isinstance(proposal_outline, dict) and "sections" in proposal_outline:
        outline_sections = [s.get("title", s.get("section_title", "")) for s in proposal_outline["sections"]]
    
    generated_titles = [s.get("section_title", s.get("title", "")) for s in concatenated_sections]
    
    prompt = f"""You are an assistant that generates a proposal document.

Given this proposal outline with {len(outline_sections)} sections:
Sections needed: {outline_sections}

And previously generated sections ({len(generated_titles)} sections):
Generated so far: {generated_titles}

Decide if you should continue generating more sections or finish.

Return a JSON object with this EXACT structure:
{{
    "should_continue": true,
    "reason": "Still missing sections: [list missing sections]"
}}

OR

{{
    "should_continue": false,
    "reason": "All sections have been generated"
}}

Rules:
- Continue (true) if not all sections from the outline have been generated
- Finish (false) if all sections from the outline are present in generated sections
- Return ONLY valid JSON"""

    return prompt
