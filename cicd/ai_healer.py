import os
import sys
import google.generativeai as genai

def analyze_build():
    # 1. Setup API Key from Jenkins Environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] AI Agent: GEMINI_API_KEY not found in environment.")
        return

    genai.configure(api_key=api_key)
    
    # 2. Identify the Log File
    log_file = sys.argv[1] if len(sys.argv) > 1 else "build_error.log"
    
    if not os.path.exists(log_file):
        print(f"[ERROR] AI Agent: Log file '{log_file}' not found.")
        return

    # 3. Read the Build Error
    with open(log_file, "r") as f:
        error_content = f.read()

    print(f"--- AI Agent: Analyzing {log_file} ---")

    # 4. Prompt Engineering for SRE Context
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""
    You are an expert SRE and DevOps Engineer. 
    A Jenkins build for the project 'Aether-Track' just failed. 
    
    Below is the error log:
    {error_content[-2000:]} 
    
    Please provide:
    1. ROOT CAUSE: What exactly went wrong?
    2. THE FIX: The specific code change or command needed to fix this.
    3. PREVENTION: One sentence on how to avoid this in the future.
    
    Keep the tone professional and concise.
    """

    # 5. Generate and Print Response
    try:
        response = model.generate_content(prompt)
        print("\n" + "="*50)
        print("💡 AI-POWERED REMEDIATION STRATEGY")
        print("="*50)
        print(response.text)
        print("="*50 + "\n")
    except Exception as e:
        print(f"[ERROR] AI Agent: Failed to reach Gemini API. {str(e)}")

if __name__ == "__main__":
    analyze_build()
