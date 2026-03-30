import os
import json
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm.prompts import (
    generate_structure_prompt,
    regenerate_structure_prompt,
    generate_section_prompt,
    regenerate_section_prompt,
    continue_or_finish_prompt,
)

load_dotenv()

class LLMClient:
    def __init__(self, model_name: str = "gpt-5", temperature: float = 0.8):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_retries=3,
            request_timeout=180
        )
        self.json_parser = JsonOutputParser()
        
        # Create a reusable prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert proposal writer. Always respond with valid JSON."),
            ("human", "{prompt}")
        ])
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """Generate response with automatic retry and JSON parsing using LangChain."""
        
        for attempt in range(max_retries):
            try:
                # Create the chain with explicit JSON instruction
                enhanced_prompt = f"{prompt}\n\nRemember: Return ONLY a valid JSON object. Do not include any text before or after the JSON."
                chain = self.prompt_template | self.llm | self.json_parser
                
                # Invoke the chain
                result = chain.invoke({"prompt": enhanced_prompt})
                
                # Validate the result has the expected structure
                if isinstance(result, dict):
                    # Check if it has sections key (even if empty)
                    if "sections" in result:
                        print(f"✓ Attempt {attempt + 1}: Valid JSON with sections array received")
                        return result
                    else:
                        # Try to fix the structure
                        print(f"⚠ Attempt {attempt + 1}: JSON missing 'sections' key, attempting to fix...")
                        fixed_result = self._fix_structure(result)
                        if "sections" in fixed_result:
                            print(f"✓ Structure fixed successfully")
                            return fixed_result
                        print(f"✗ Attempt {attempt + 1}: Could not fix structure")
                else:
                    print(f"✗ Attempt {attempt + 1}: Response is not a dict")
                    
            except OutputParserException as e:
                print(f"✗ Attempt {attempt + 1}: JSON parsing failed - {str(e)[:100]}")
                if attempt == max_retries - 1:
                    # Last attempt - try to extract JSON manually
                    try:
                        raw_response = self.prompt_template | self.llm
                        raw_result = raw_response.invoke({"prompt": enhanced_prompt})
                        # Try to extract JSON from the response
                        import re
                        json_match = re.search(r'\{.*\}', raw_result.content, re.DOTALL)
                        if json_match:
                            parsed = json.loads(json_match.group())
                            return self._fix_structure(parsed)
                    except Exception as final_e:
                        print(f"✗ Final attempt failed: {final_e}")
                        
            except Exception as e:
                print(f"✗ Attempt {attempt + 1}: Error - {str(e)[:100]}")
                
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        # Return fallback response
        print("✗ All attempts failed, returning fallback")
        return {
            "error": "Failed to generate response after all retries",
            "proposal_title": "Generated Proposal",
            "sections": [],
            "overall_strategy": "Default strategy",
            "strengths_to_highlight": [],
            "potential_challenges": []
        }
    
    def _fix_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Try to fix malformed structure to match expected format."""
        if "sections" in result:
            return result
        
        # Look for section-like objects in the response
        sections = []
        for key, value in result.items():
            if isinstance(value, dict):
                # Check if this looks like a section
                if "description" in value or "section_title" in value:
                    section = value.copy()
                    if "title" not in section:
                        section["title"] = section.get("section_title", key)
                    sections.append(section)
            elif isinstance(value, list) and len(value) > 0:
                # Check if this is a list of sections
                if isinstance(value[0], dict) and ("title" in value[0] or "section_title" in value[0]):
                    sections = value
                    break
        
        if sections:
            result["sections"] = sections
        else:
            result["sections"] = []
        
        return result
    
    def generate_structure(self, rfp_text: str, template_text: str, 
                          additional_docs: List[Dict[str, str]], 
                          user_instructions: str = "") -> Dict[str, Any]:
        """Generate proposal structure based on RFP and template."""
        
        # Use the centralized prompt function
        prompt = generate_structure_prompt(rfp_text, template_text, additional_docs, user_instructions)
        
        # Use LangChain for generation with retry and parsing
        return self._generate_with_retry(prompt)
    
    def regenerate_structure(self, rfp_text: str, template_text: str, 
                           proposal_outline: Dict[str, Any], 
                           user_feedback: str) -> Dict[str, Any]:
        """Regenerate proposal structure based on user feedback."""
        
        # Use the centralized prompt function
        prompt = regenerate_structure_prompt(rfp_text, template_text, proposal_outline, user_feedback)
        
        # Use LangChain for generation with retry and parsing
        return self._generate_with_retry(prompt)
    
    def generate_section(self, proposal_outline: Dict[str, Any], 
                        concatenated_sections: List[Dict[str, str]], 
                        user_instructions: str = "",
                        rfp_text: str = "",
                        template_text: str = "",
                        section_to_generate: str = "",
                        section_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate section content based on proposal outline and previous sections."""
        
        # Use the centralized prompt function with specific section info
        prompt = generate_section_prompt(
            proposal_outline, 
            section_to_generate,  # Specific section title to generate
            concatenated_sections, 
            rfp_text, 
            template_text, 
            None, 
            user_instructions
        )
        
        # Add section details to the prompt if available
        if section_details:
            use_template = section_details.get("use_template_content", False)
            prompt += f"\n\nSECTION TO GENERATE: {section_to_generate}"
            prompt += f"\nUSE_TEMPLATE_CONTENT: {use_template}"
            if use_template:
                prompt += f"\nACTION: Find '{section_to_generate}' in the template above and copy its content EXACTLY."
            else:
                prompt += f"\nACTION: Generate NEW content for '{section_to_generate}' based on RFP requirements."
        
        # Use LangChain for generation with retry and parsing
        return self._generate_with_retry(prompt)
    
    def regenerate_section(self, proposal_outline: Dict[str, Any], 
                          concatenated_sections: List[Dict[str, str]], 
                          current_section: Dict[str, str], 
                          user_feedback: str) -> Dict[str, Any]:
        """Regenerate section content based on user feedback."""
        
        # Use the centralized prompt function
        prompt = regenerate_section_prompt(proposal_outline, current_section, user_feedback, concatenated_sections, "", "")
        
        # Use LangChain for generation with retry and parsing
        return self._generate_with_retry(prompt)
    
    def decide_continue(self, proposal_outline: Dict[str, Any], 
                       concatenated_sections: List[Dict[str, str]]) -> bool:
        """Decide whether to continue generating sections or finish."""
        
        # Use the centralized prompt function for LLM-based decision
        prompt = continue_or_finish_prompt(proposal_outline, concatenated_sections, "", "")
        
        # Use LangChain for generation with retry and parsing
        result = self._generate_with_retry(prompt)
        
        # Handle different response formats
        if isinstance(result, dict):
            return result.get("should_continue", result.get("continue", False))
        elif isinstance(result, bool):
            return result
        else:
            # Fallback to simple logic if LLM response is unclear
            return self._fallback_continue_logic(proposal_outline, concatenated_sections)
    
    def _fallback_continue_logic(self, proposal_outline: Dict[str, Any], 
                                concatenated_sections: List[Dict[str, str]]) -> bool:
        """Fallback logic for continue decision when LLM fails."""
        # Extract section titles from outline
        outline_sections = []
        if isinstance(proposal_outline, dict):
            if "sections" in proposal_outline:
                outline_sections = [section.get("title", section.get("section_title", "")) for section in proposal_outline["sections"]]
            elif "structure" in proposal_outline:
                outline_sections = [section.get("title", section.get("section_title", "")) for section in proposal_outline["structure"]]
            else:
                # Handle different outline formats
                for key, value in proposal_outline.items():
                    if isinstance(value, dict) and ("title" in value or "section_title" in value):
                        outline_sections.append(value.get("title", value.get("section_title", "")))
        
        # Get generated section titles - handle both key names
        generated_sections = [section.get("section_title", section.get("title", "")) for section in concatenated_sections]
        
        # Check if all outline sections are generated
        should_continue = len(outline_sections) > len(generated_sections)
        
        return should_continue
