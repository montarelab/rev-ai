from langchain_chroma import Chroma
from langchain_core.tools import create_retriever_tool
from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL='qwen3:4b'
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=OllamaEmbeddings(model=EMBEDDING_MODEL),
)

# EMBEDDING_MODEL='gemini-embedding-001'
# vectorstore = Chroma(
#     collection_name="knowledge_base",
#     embedding_function=VertexAIEmbeddings(
#         model_name=EMBEDDING_MODEL
#     ),
# )


retriever = vectorstore.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_internal_knowledge",
    """
    Retrieve architectural or stylistic guidance from internal vectorized knowledge.

    Use this to evaluate whether the code conforms to internal naming conventions, architecture standards, and domain-specific logic.

    Parameters:
        query (str): A description or snippet of code to match against internal patterns.

    Returns:
        str: Closest matching convention, example, or suggestion.
    """,
)