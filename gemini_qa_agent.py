import os
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


# ==========================================
# 1. Define the Agent's Blueprint (Schema)
# ==========================================
class TestCase(BaseModel):
    test_id: str = Field(description="Unique identifier for the test case (e.g., TC-001)")
    title: str = Field(description="Short, descriptive title of the test")
    test_type: str = Field(description="Category of test (e.g., Positive, Negative, Boundary, Security, Edge Case)")
    preconditions: str = Field(description="System state or data required before executing the test")
    steps: List[str] = Field(description="Step-by-step instructions to execute the test")
    expected_result: str = Field(description="The exact outcome expected if the system functions correctly")


class TestSuite(BaseModel):
    test_cases: List[TestCase] = Field(description="A comprehensive list of generated test cases")


# ==========================================
# 2. Build the Gemini Agent
# ==========================================
def run_gemini_qa_agent(requirement_text: str, api_key: str):
    # Set the Gemini API key environment variable
    os.environ["GOOGLE_API_KEY"] = api_key

    # Initialize Gemini (UPDATED: Using gemini-3.5-flash for current API support)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)

    # Bind the Pydantic schema to Gemini to guarantee structured JSON output
    structured_llm = llm.with_structured_output(TestSuite)

    # Give the agent its QA persona and instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Senior QA Automation Engineer. 
        Your job is to thoroughly analyze user stories, requirements, or acceptance criteria, and generate a comprehensive test suite. 
        Ensure you cover positive paths, negative paths, validation checks, and critical edge cases.
        Always return your response exactly matching the requested structured format."""),
        ("human", "Generate a complete test suite for the following requirement:\n\n{requirement}")
    ])

    # Chain the prompt and the structured LLM together
    agent_chain = prompt | structured_llm

    print("🤖 Gemini Agent is analyzing requirements and writing test cases...")
    # Invoke the agent
    return agent_chain.invoke({"requirement": requirement_text})


# ==========================================
# 3. Run the Agent (Execution)
# ==========================================
if __name__ == "__main__":
    # Insert your actual Google Gemini API key here
    MY_GEMINI_API_KEY = ""

    sample_requirement = """
    User Story: As a user, I want to be able to reset my password using my email address so that I can regain access to my account if I forget my password.

    Acceptance Criteria:
    1. User enters email and clicks 'Send Reset Link'.
    2. If the email exists in our database, send a reset link to that email.
    3. If the email does NOT exist, show a generic 'If your email is in our system, a link has been sent' message to prevent email enumeration attacks.
    4. The reset link must expire in exactly 15 minutes.
    """

    try:
        # Run the agent
        test_suite = run_gemini_qa_agent(sample_requirement, MY_GEMINI_API_KEY)

        # Format and print the results to your terminal
        print("\n✅ Test Suite Generated Successfully by Gemini!\n")
        for tc in test_suite.test_cases:
            print(f"--- {tc.test_id}: {tc.title} [{tc.test_type}] ---")
            print(f"Preconditions: {tc.preconditions}")
            print("Steps:")
            for i, step in enumerate(tc.steps, 1):
                print(f"  {i}. {step}")
            print(f"Expected Result: {tc.expected_result}\n")

    except Exception as e:
        print(f"❌ Error running Gemini agent: {e}")