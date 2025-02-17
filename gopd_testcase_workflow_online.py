# 外部ライブラリをインポート
from multiprocessing import context
import streamlit as st
from langchain_aws import ChatBedrock
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

myprompt = """
<instruction>
Please answer my request based on {context} and regarding document of {question}. You are an expert financial software analyst specializing in T24 core banking systems. Your task is to analyze documents described core banking operations for MUFG Bank using the T24 console, and generate structured output based on the document's content.
</instruction>

<context>
The {question} document typically contains the following categories:
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
1. Analyze the document of {question} thoroughly.
2. Create a {question} UAT test case table with columns: No, Pre-Requirements, Use-Case, and Expected Result.
3. Develop a TO-BE requirement document based on the input.
4. Create a detailed workflow description, focusing on the Business Solution and Mockup categories.
</task>

<output_format>
Please structure your output as follows:
1. UAT Test Case as Table format by HTML
2. Workflow Description by text by Graphviz
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

# 検索手段を指定
retriever = AmazonKnowledgeBasesRetriever(
    # knowledge_base_id="UKMLCBEWCN",  # ここにナレッジベースIDを記載する
    knowledge_base_id="HVSKVGQLIX", # GOPD-All-Data
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
)

# プロンプトのテンプレートを定義
# prompt = ChatPromptTemplate.from_template(
#     # "以下のcontextに基づいて回答してください: {context} / 質問: {question}"
#     myprompt
# )
prompt = ChatPromptTemplate.from_template(myprompt)

# LLMを指定
model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"max_tokens": 4000},
)

# チェーンを定context義（検索 → プロンプト作成 → LLM呼び出し → 結果を取得）
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# Streamlit version
# フロントエンドを記述
st.title("MUFG GOPDF PoC on AWS: RAG for Testcase")
question = st.text_input("Entry the code of JIRA Code for Testcase.")
button = st.button("Generate!")

# ボタンが押されたらチェーン実行結果を表示
if button:
    st.write(chain.invoke(question))


