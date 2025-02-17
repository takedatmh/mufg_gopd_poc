# 外部ライブラリをインポート
from itertools import chain
from multiprocessing import context
import sys
from langchain_aws import AmazonKnowledgeBasesRetriever, ChatBedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os

myprompt = """
<instruction>
Please answer my request based on {context} and regarding document of {jira_code}. You are an expert financial software analyst specializing in T24 core banking systems. Your task is to analyze documents described core banking operations for MUFG Bank using the T24 console, and generate structured output based on the document's content.
</instruction>

<context>
The {jira_code} document typically contains the following categories:
<categories>
  <category name="Background">
    <description>AS-IS MUFG Bank's process, AS-IS T24 Initial condition (console items and functions), TO-BE T24 Process condition (implemented MUFG bank's business requirements)</description>
  </category>
  <category name="Requirement Description">
    <description>MUFG Bank's business requirements for the specific business scope</description>
  </category>
  <category name="Existing Functionality">
    <description>Current functions of T24</description>
  </category>
  <category name="Gap Description">
    <description>Gaps between T24 initial function and MUFG business requirements, aligning with new function implementations</description>
  </category>
  <category name="Business Solution">
    <description>Required new functions and T24 console operation flow after implementing requirements</description>
  </category>
  <category name="Mockup Screen">
    <description>Implemented T24 console mockup images and descriptions, including new functions and their operation</description>
  </category>
  <category name="Flow Diagram">
    <description>Workflow diagram images (if available)</description>
  </category>
  <category name="Open Clarification">
    <description>Usually NA</description>
  </category>
  <category name="Assumption &amp; Exclusions">
    <description>Specific pre-conditions, out of scope items, etc.</description>
  </category>
  <category name="Functional Requirements">
    <description>T24 functions after implementing MUFG requirements</description>
  </category>
  <category name="Non-Functional Requirements">
    <description>Performance, Reliability, cost, etc.</description>
  </category>
  <category name="Dependencies and Exclusions">
    <description>Dependency functions</description>
  </category>
  <category name="Test Case">
    <description>User Acceptance Test scripts in table format (Use Case Ref Number, User Case description, Expected Result)</description>
  </category>
</categories>
</context>

<task>
1. Analyze the document of {jira_code} thoroughly.
2. Deep Understading "Requiremnt Description", these requirements are simmiler to the result or expectation of UAT test cases.
3. Deep understanding "Business Sollution", there solution is simmilar to UAT Use-Case description. And "Mockup Screen" console has these solution and are operated by these solution.
2. Create a {jira_code} UAT test case table with columns: No, Pre-Requirements, Use-Case, and Expected Result as html file.
3. When you create UAT test case, please use each document's descriptin of Mockup Screen. Usualy, this item has T24 console iamages and descriptions of this console operation. Please understnad console operation requirements and refer this information for creation of UAT test case of Use-Case description.
</task>

<output_format>
Please structure your output as follows:
1. UAT Test Case as Table format with pink boarder line by HTML
</output_format>

<additional_instructions>
- In the JSON structure, use the category names as keys and provide detailed content for each.
- For the UAT test case table, ensure each row corresponds to a gap identified in the Gap Description, with the Use-Case describing the operation of the new function and the Expected Result aligning with MUFG requirements.
- In the workflow description, clearly distinguish between actors, actions, and goals (both success and failure scenarios).
- When describing mockups, explain what each console element represents, identify new functions/items, and detail how they operate.
- If any information is unclear or missing, state your assumptions clearly.
</additional_instructions>

<output_language>
English
</output_language>

<max_output_tokens>4000</max_output_tokens>
"""

# チェーンを定義（検索 → プロンプト作成 → LLM呼び出し → 結果を取得）
def generate_Testcase_workflow(jira_code):
    # 検索手段を指定
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="HVSKVGQLIX", # GOPD-All-Data
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
    )

    # プロンプトのテンプレートを定義
    prompt = ChatPromptTemplate.from_template(myprompt)

    # LLMを指定
    model = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"max_tokens": 4000},
    )
 
    # チェーンを定義（検索 → プロンプト作成 → LLM呼び出し → 結果を取得）
    chain = (
        {"context": retriever, "jira_code": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    # Batch execution
    result = chain.invoke(jira_code)

    # Output
    write_to_file(f"{jira_code}.html", result)

# File writer
def write_to_file(filename, content):
  output_dir = "./testcase"
  try:
    os.makedirs(output_dir, exist_ok=False)
  except FileExistsError:
    print(f"Directory {output_dir} already exists.")
  except Exception as e:
    print(f"An error occurred while creating the directory: {e}")
    return

  filepath = os.path.join(output_dir, filename)
  try:
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)
  except Exception as e:
    print(f"An error occurred while writing to the file: {e}")

# メイン関数
def main():
    if len(sys.argv) < 2:
        print("Usage: python 1_rag_for_testcase_batch.py <JIRA Code1> [<JIRA Code2> ...]")
        sys.exit(1)
    jira_codes = sys.argv[1:]
    print(f"The number of args: {len(jira_codes)}")
    for jira_code in jira_codes:
        print(f"Processing JIRA Code: {jira_code}")
        generate_Testcase_workflow(jira_code)
        print(f"Text generation for {jira_code} is complete.")

if __name__ == "__main__":
    main()


