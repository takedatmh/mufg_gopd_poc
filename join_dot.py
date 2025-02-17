# 必要なライブラリのインポート
from itertools import chain
from multiprocessing import context
import sys
from langchain_aws import AmazonKnowledgeBasesRetriever, ChatBedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os

#1. Read all dot files in the designated directory as dir.
def read_dot_files(dir):
    dots = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".dot"):
                dots.append(os.path.join(root, file))
    return dots

#2. Open dot file as text and store into array. Then return text[].
def open_dot_file_as_text(dots):
    text = []
    for dot in dots:
        with open(dot, "r", encoding="utf-8") as f:
            content = f.read()
            # print(content) #Debug
            text.append(content)
    return text

#3 Combine dots_txt[] into a single text file with "\n".
def combine_dot_files(input_dot_txt) -> str:
    combined_dot = ""
    for dot in input_dot_txt:
        combined_dot += "\n" + "\n" + dot
    return combined_dot
    # return "\n".join(input_dot_txt)

#4. LLM read each dot file and join each graph, if each graph has same semantic node or edges.
class JoinDotFiles:

    def __init__(self, input_dot_txt):
        self.input_dot_txt = input_dot_txt

    #3.2 Run the LLM to join the graphs.
    def run(self):

        # プロンプトのテンプレートを定義
        SystemMessagePrompt = """
        You are a processional of graphviz dot file format. 
        Then, your are a professional of the banking business operation baesed on 
        {context} data and the general knowledge of the banking business operation.
        """
        humanMessagePropmpt = """
        You are an AI assistant that can read and understand Graphviz dot file formats. 
        Your task is to:
        1. Read provided dot files' script {input_dot_txt} and understand these graphs as workflow based on {"context"}.
        2. If you can join these graphs as workflow, please join it as a singale graph.
        3. Generate a new dot file that contains the joined graph.
        """

        # 検索手段を指定
        retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id="HVSKVGQLIX",  # GOPD-All-Data
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SystemMessagePrompt),
            ("human", humanMessagePropmpt)
        ])

        # LLMを指定
        model = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"max_tokens": 4092},
        )

        # Chainを定義
        chain = prompt | model | StrOutputParser()

        # チェーンを実行
        result = chain.invoke({"context": retriever, "input_dot_txt": "input_data"})   
        return result

#4. Main function to run the program.
def main():
    dir_path = './workflow/Branch-Operations-Manual-for-Deposit-March-2021-chapter1'
    dots = read_dot_files(dir_path)
    dots_txt = open_dot_file_as_text(dots)
    joinDotFiles = JoinDotFiles(combine_dot_files(dots_txt))
    result = joinDotFiles.run()
    print(result)

if __name__ == "__main__":
    main()

def sample(input):
    # 検索手段を指定
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="HVSKVGQLIX", # GOPD-All-Data
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
    )

    # テンプレート文章を定義し、プロンプトを作成
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional of the banking business operation based on {context} data and the general knowledge of the banking business operation."),
        ("user", "Please join the following graphviz graphs as a dot file, if these graphs as connection points or same actor nodes. \n{input}")
    ])

    # LLMを指定
    model = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"max_tokens": 4092},
    )

    # LLMのAPIにこのプロンプトを送信するためのチェーンを作成
    chain = prompt | model | StrOutputParser()

    # チェーンを実行し、結果を表示
    # print(chain.invoke({"context": retriever,"input": input}))
    ret = chain.invoke({"context": retriever,"input": input})
    print("####RET: {}".format(ret))

    return ret
