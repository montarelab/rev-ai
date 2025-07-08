from langchain_chroma import Chroma
from langchain_core.tools import create_retriever_tool, Tool
from langchain_openai import OpenAIEmbeddings

from config import Config


def get_retriever_tool_description():
    return """
        Retrieve architectural or stylistic guidance from internal vectorized knowledge.

        Use this to evaluate whether the code conforms to internal naming conventions, architecture standards, and domain-specific logic.

        Parameters:
            query (str): A description or snippet of code to match against internal patterns.

        Returns:
            str: Closest matching convention, example, or suggestion.
    """

def get_retriever_tool(config: Config) -> Tool:

    vectorstore = Chroma(
        collection_name="knowledge_base",
        embedding_function=OpenAIEmbeddings(
            model=config.embedding_model,
            api_key=config.api_key
        ),
    )

    retriever = vectorstore.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_internal_knowledge",
        get_retriever_tool_description(),
    )

    return retriever_tool