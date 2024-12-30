from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


from dotenv import load_dotenv
import os
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


def generate_embeddings_from_web(links):
    loader = WebBaseLoader(links,bs_kwargs= dict(
                           parse_only = bs4.SoupStrainer('main' ,class_ = ('course')) #filters the class from the page
                       ))
    documents = loader.load()

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    final_documents = text_splitter.split_documents(documents)

    # Generate embeddings
    model_name = "sentence-transformers/all-mpnet-base-v2"
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )

    # Create FAISS vector store
    db = FAISS.from_documents(final_documents, hf)
    return db

def generate_embeddings_from_excel():
    loader = UnstructuredExcelLoader("AV_Free_Courses.xlsx")
    documents = loader.load()

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    final_documents = text_splitter.split_documents(documents)

    # Generate embeddings
    model_name = "sentence-transformers/all-mpnet-base-v2"
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )

    # Create FAISS vector store
    db = FAISS.from_documents(final_documents, hf)
    return db


def generate_response(db_web,db_excel,query):
    # Combine retrievers from both vector databases
    retriever_web = db_web.as_retriever()
    retriever_excel = db_excel.as_retriever()

    # Create combined retriever
    combined_docs = retriever_web.get_relevant_documents(query) + retriever_excel.get_relevant_documents(query)

    llm = ChatGroq(groq_api_key = GROQ_API_KEY, model_name = 'llama3-8b-8192')

    # Create the prompt based on the content and the query
    prompt=ChatPromptTemplate.from_template(
        """
        You are a helpful assistant designed to guide users in finding the best free online courses. For each user query:
1. Determine the learning objectives based on the query.
2. Retrieve the most relevant courses from the provided context.
3. Rank the courses according to relevance based on the following criteria:
   - Course topic (e.g., machine learning, data analysis)
   - Course level (e.g., beginner, intermediate)
   - How well the course matches the user's needs (e.g., practical applications, theory)

For each course, output:
- **Title**: [Course title]
- **Brief Description**: [Short, informative description]
- **Core Topics**: [Major topics covered]
- **Difficulty Level**: [e.g., Beginner, Intermediate, Advanced]

If the user asks for an overview (e.g., "How many machine learning courses are there?"), provide the total number of relevant courses and suggest a few options based on the query.

Context: {context}

Query: {input}

        """
    )

    # implement openai call logic and get back the response
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    response = question_answer_chain.invoke({'context': combined_docs, 'input': query})
    return response
