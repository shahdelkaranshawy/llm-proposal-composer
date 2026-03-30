"""
Proposal Composer - Main Entry Point

This application helps users create professional proposals by:
1. Extracting text from RFP and template documents
2. Generating structured proposal outlines using LLM
3. Allowing user review and feedback on structure
4. Generating section content iteratively
5. Allowing review, reordering, and deletion of sections
6. Exporting final proposal as Word document

Run with: streamlit run main.py
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install requirements. Please install manually:")
        print("pip install streamlit langgraph langchain openai python-docx PyPDF2 python-dotenv")

def main():
    """Main entry point."""
    print("Starting Proposal Composer...")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Please create one with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    
    # Run Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\nShutting down Proposal Composer...")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
