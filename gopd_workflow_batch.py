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
As an expert in core banking operations at MUFG Bank, a major Japanese mega-bank, your task is to understand the provided document(s) on core banking procedures and create workflow diagrams to represent the processes. The core banking operations include deposits, remittances (high value, low value), lending, import/export, accounting, information systems, and common business activities that make up the financial services.
While the detailed structure of the procedure documents may vary by country, they typically include chapters that describe the procedures for each core banking business. Your task is to thoroughly understand the provided document(s) and create workflow diagrams, with swimlanes for each actor, to represent the business processes. The output should be in the Graphviz .dot file format.
For any unclear actors, use "Unknown" as the actor name. The diagram nodes should represent operations, actions, or conditional decisions (represented as diamond shapes). The edges should be directed graphs with "Yes" or "No" attributes, displayed as solid and dashed lines respectively. The workflows should be structured as directed acyclic graphs, starting and ending with appropriate nodes.
</instruction>

<context>
MUFG Bank has created detailed procedure documents for core banking operations in each country where it operates. These documents serve as the basis for executing core banking activities, which include:

    Deposits
    Remittances (high value, low value)
    Lending
    Import/Export
    Accounting
    Information Systems
    Common business activities

While the specific structure of these procedure documents may vary by country, they generally follow a chapter-based format, with each chapter describing the procedures for a particular core banking business.
</context>

<task>

    Thoroughly understand the provided document(s) {context} and designateed document(s) {jira_code} on core banking procedures.
    Create workflow diagrams to represent the business processes described in the document(s).
    Output the diagrams in the Graphviz .dot file format. </task>

<output_format>
The output should be a Graphviz .dot file containing the workflow diagrams for designated document {jira_code}.
</output_format>

<additional_instructions>

    For any unclear actors, use "Unknown" as the actor name.
    The diagram nodes should represent operations, actions, or conditional decisions (represented as diamond shapes).
    The edges should be directed graphs with "Yes" or "No" attributes.
    The workflows should be structured as directed acyclic graphs, starting and ending with appropriate nodes.
    Each node should belong to the swimlane of its respective actor. 
    Start and End node shape is created as the circle shape.
    "dot" file does not have any comment description in the file.
    
</additional_instructions>´

<output_language>
English
</output_language>

<max_output_tokens>4092</max_output_tokens>
"""

# チェーンを定義（検索 → プロンプト作成 → LLM呼び出し → 結果を取得）
def generate_Testcase_workflow(jira_code):
    # 検索手段を指定
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="HVSKVGQLIX", # GOPD-All-Data
      # knowledge_base_id="5USBLOWYWF", #GraphRAG-HK-Deposit-manual
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
    )

    # プロンプトのテンプレートを定義
    prompt = ChatPromptTemplate.from_template(myprompt)

    # LLMを指定
    model = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"max_tokens": 4092},
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
    write_to_file(f"{jira_code}.dot", result)

# File writer
def write_to_file(filename, content):
  output_dir = "./workflow"
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

# File writer wtih dir_path
def write_to_file(filename, content, dir_path):
  output_dir = dir_path
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


# omazinai
if __name__ == "__main__":
    main()


