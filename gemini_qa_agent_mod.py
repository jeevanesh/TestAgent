import os
import csv
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
    os.environ["GOOGLE_API_KEY"] = api_key

    # Using the current, active model
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
    structured_llm = llm.with_structured_output(TestSuite)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Senior QA Automation Engineer. 
        Your job is to thoroughly analyze user stories, requirements, or acceptance criteria, and generate a comprehensive test suite. 
        Ensure you cover positive paths, negative paths, validation checks, and critical edge cases.
        Always return your response exactly matching the requested structured format."""),
        ("human", "Generate a complete test suite for the following requirement:\n\n{requirement}")
    ])

    agent_chain = prompt | structured_llm

    print("🤖 Gemini Agent is analyzing requirements and writing test cases...")
    return agent_chain.invoke({"requirement": requirement_text})


# ==========================================
# 3. Exporter Functions (.CSV and .MD)
# ==========================================
def export_to_csv(test_cases: List[TestCase], filename: str = "test_suite.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(["Test ID", "Title", "Type", "Preconditions", "Steps", "Expected Result"])

        # Write data
        for tc in test_cases:
            # Join the list of steps into a single string with line breaks
            steps_str = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(tc.steps)])
            writer.writerow([tc.test_id, tc.title, tc.test_type, tc.preconditions, steps_str, tc.expected_result])

    print(f"📄 Saved CSV to: {os.path.abspath(filename)}")


def export_to_markdown(test_cases: List[TestCase], filename: str = "test_suite.md"):
    with open(filename, mode='w', encoding='utf-8') as file:
        file.write("# Auto-Generated QA Test Suite\n\n")

        for tc in test_cases:
            file.write(f"## {tc.test_id}: {tc.title}\n")
            file.write(f"- **Type:** {tc.test_type}\n")
            file.write(f"- **Preconditions:** {tc.preconditions}\n")
            file.write("- **Steps:**\n")
            for i, step in enumerate(tc.steps, 1):
                file.write(f"  {i}. {step}\n")
            file.write(f"- **Expected Result:** {tc.expected_result}\n\n")
            file.write("---\n\n")

    print(f"📝 Saved Markdown to: {os.path.abspath(filename)}")


# ==========================================
# 4. Run the Agent & Export Files
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
        # 1. Run the agent to generate the data
        test_suite = run_gemini_qa_agent(sample_requirement, MY_GEMINI_API_KEY)
        print("\n✅ Test Suite Generated Successfully!\n")

        # 2. Export the data to CSV
        export_to_csv(test_suite.test_cases, "test_cases.csv")

        # 3. Export the data to Markdown
        export_to_markdown(test_suite.test_cases, "test_cases.md")

        print("\n🎉 All files have been created in your project folder.")

    except Exception as e:
        print(f"❌ Error running Gemini agent: {e}")