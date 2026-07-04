import os
import csv
import datetime
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load variables from the .env file automatically
load_dotenv()


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
def run_gemini_qa_agent(requirement_text: str):
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file.")

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
# 3. File Helpers (Read & Export)
# ==========================================
def read_requirements_file(filename: str = "requirements.md") -> str:
    """Reads the requirements text from a local markdown file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                raise ValueError("The file is empty.")
            return content
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find '{filename}' in the current directory.")
        print("Please create this file and paste your user stories/requirements into it before running the script.")
        return None
    except Exception as e:
        print(f"\n❌ Error reading {filename}: {e}")
        return None


def export_to_csv(test_cases: List[TestCase], filename: str):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Test ID", "Title", "Type", "Preconditions", "Steps", "Expected Result"])

        for tc in test_cases:
            steps_str = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(tc.steps)])
            writer.writerow([tc.test_id, tc.title, tc.test_type, tc.preconditions, steps_str, tc.expected_result])
    print(f"📄 Saved CSV to: {os.path.abspath(filename)}")


def export_to_markdown(test_cases: List[TestCase], filename: str):
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
# 4. Run the Agent Workflow
# ==========================================
if __name__ == "__main__":

    # 1. Read from the external file
    print("📖 Reading requirements.md...")
    requirements = read_requirements_file("requirements.md")

    # Only proceed if we successfully read the file
    if requirements:
        try:
            # 2. Run the AI agent
            test_suite = run_gemini_qa_agent(requirements)
            print("\n✅ Test Suite Generated Successfully!\n")

            # 3. Create unique filenames using timestamps
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"test_cases_{timestamp}.csv"
            md_filename = f"test_cases_{timestamp}.md"

            # 4. Export the data
            export_to_csv(test_suite.test_cases, csv_filename)
            export_to_markdown(test_suite.test_cases, md_filename)

            print("\n🎉 All files have been created securely in your project folder.")

        except PermissionError:
            print(
                "\n❌ PERMISSION ERROR: Please close the Excel or Markdown file if it is currently open, then try again.")
        except Exception as e:
            print(f"\n❌ Error running Gemini agent: {e}")