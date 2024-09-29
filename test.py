# import os
# from typing import List, Dict
# import google.generativeai as genai
# from dotenv import load_dotenv
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.docstore.document import Document
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# # Configuration
# GOOGLE_API_KEY = "AIzaSyDFzmzC_BGvnaTVAYCgUULsr4AL00mJN7Q"
# PDF_PATHS = ["C:/Users/nirde/Downloads/Vipul Sharma Provisional Offer Letter.pdf","C:/Users/nirde/Downloads/CV_Vipul_Sharma (1).pdf"]
# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 200
# EMBEDDING_MODEL = 'models/embedding-001'
# GENERATIVE_MODEL = 'gemini-pro'

# # Set up Gemini API
# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it before running the script.")

# genai.configure(api_key=GOOGLE_API_KEY)

# class PDFLoader:
#     @staticmethod
#     def load_pdfs(pdf_paths: List[str]) -> List[Document]:
#         documents = []
#         for path in pdf_paths:
#             try:
#                 loader = PyPDFLoader(path)
#                 documents.extend(loader.load())
#             except Exception as e:
#                 print(f"Error loading PDF {path}: {e}")
#         if not documents:
#             raise ValueError("No documents were successfully loaded. Please check your PDF paths and file permissions.")
#         return documents

# class DocumentSplitter:
#     @staticmethod
#     def split_documents(documents: List[Document]) -> List[Document]:
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
#         return text_splitter.split_documents(documents)

# class VectorStore:
#     @staticmethod
#     def create(documents: List[Document]) -> FAISS:
#         embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
#         return FAISS.from_documents(documents, embeddings)

#     @staticmethod
#     def query(vector_store: FAISS, query: str, k: int = 4) -> List[Document]:
#         return vector_store.similarity_search(query, k=k)

# class ResponseGenerator:
#     @staticmethod
#     def generate(query: str, context: str) -> str:
#         llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
#         prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
#         response = llm.invoke(prompt)
#         return response.content

# class ChatBot:
#     def __init__(self, vector_store: FAISS):
#         self.vector_store = vector_store
#         self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=GOOGLE_API_KEY)

#     def get_general_response(self, query: str) -> str:
#         prompt = f"Answer the following question to the best of your ability. If you're not sure or the question requires specific information not provided, respond with 'I need more context to answer that accurately.'\n\nQuestion: {query}\n\nAnswer:"
#         response = self.llm.invoke(prompt)
#         return response.content

#     def get_pdf_specific_response(self, query: str) -> str:
#         relevant_docs = VectorStore.query(self.vector_store, query)
#         context = "\n".join([doc.page_content for doc in relevant_docs])
#         prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
#         response = self.llm.invoke(prompt)
#         return response.content

#     def chat_loop(self):
#         print("Chat with your AI assistant! (Type 'exit' to quit)")
#         while True:
#             query = input("You: ")
#             if query.lower() == 'exit':
#                 break
            
#             try:
#                 general_response = self.get_general_response(query)
#                 if "I need more context" in general_response:
#                     response = self.get_pdf_specific_response(query)
#                 else:
#                     response = general_response
#                 print("AI:", response)
#             except Exception as e:
#                 print(f"An error occurred: {e}")

# def main():
#     try:
#         # Load and process documents
#         documents = PDFLoader.load_pdfs(PDF_PATHS)
#         if not documents:
#             raise ValueError("No documents were loaded. Please check your PDF paths and file permissions.")
        
#         split_docs = DocumentSplitter.split_documents(documents)
        
#         # Create vector store
#         vector_store = VectorStore.create(split_docs)
        
#         # Start chat bot
#         chat_bot = ChatBot(vector_store)
#         chat_bot.chat_loop()
#     except Exception as e:
#         print(f"An error occurred during setup: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()

import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import pyaudio
import wave
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain

load_dotenv()

# Configuration
GOOGLE_API_KEY = "AIzaSyDFzmzC_BGvnaTVAYCgUULsr4AL00mJN7Q"
PDF_PATHS = ["C:/Users/nirde/Downloads/Vipul Sharma Provisional Offer Letter.pdf","C:/Users/nirde/Downloads/CV_Vipul_Sharma (1).pdf"]
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = 'models/embedding-001'
GENERATIVE_MODEL = 'gemini-pro'

# Add PostgreSQL configuration
DB_NAME = "sample"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# Set up Gemini API
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it before running the script.")

genai.configure(api_key=GOOGLE_API_KEY)

# Update Sarvam AI API configuration
SARVAM_API_KEY = "88516a50-94d0-48d3-b587-7ed098757463"
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"

def record_audio(duration=5, sample_rate=44100, chunk=1024, channels=1):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print(f"Recording for {duration} seconds...")
    frames = []

    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save as WAV file
    wf = wave.open("temp_audio.wav", "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()  # Explicitly close the wave file

    return "temp_audio.wav"

def speech_to_text() -> str:
    headers = {
        'api-subscription-key': SARVAM_API_KEY,
    }
    
    print("Press Enter to start recording...")
    input()
    
    audio_file = record_audio()
    
    files = {
        'file': ('audio.wav', open(audio_file, 'rb'), 'audio/wav')
    }
    
    data = {
        'model': 'saaras:v1',
        'prompt': ''  # You can add a prompt if needed
    }

    try:
        print(f"Sending request to {SARVAM_API_URL}")
        response = requests.post(SARVAM_API_URL, headers=headers, data=data, files=files)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(result)
        return result.get('transcript', '')  # Changed from 'text' to 'transcript'
    except requests.exceptions.RequestException as e:
        print(f"Error in speech-to-text conversion: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.content}")
        return ''
    finally:
        files['file'][1].close()  # Close the file object
        try:
            os.remove(audio_file)  # Clean up the temporary audio file
        except PermissionError:
            print(f"Warning: Could not delete temporary file {audio_file}")

class PDFLoader:
    @staticmethod
    def load_pdfs(pdf_paths: List[str]) -> List[Document]:
        documents = []
        for path in pdf_paths:
            try:
                loader = PyPDFLoader(path)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading PDF {path}: {e}")
        if not documents:
            raise ValueError("No documents were successfully loaded. Please check your PDF paths and file permissions.")
        return documents

class DocumentSplitter:
    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        return text_splitter.split_documents(documents)

class VectorStore:
    @staticmethod
    def create(documents: List[Document]) -> FAISS:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        return FAISS.from_documents(documents, embeddings)

    @staticmethod
    def query(vector_store: FAISS, query: str, k: int = 4) -> List[Document]:
        return vector_store.similarity_search(query, k=k)

class TextDatabase:
    def __init__(self):
        self.data = {
            "company_info": "Our company, TechCorp, was founded in 2010 and specializes in AI solutions.",
            "product_lineup": "We offer three main products: AI Assistant, Smart Analytics, and AutoML Platform.",
            "contact_details": "You can reach us at contact@techcorp.com or call 1-800-TECH-CORP."
        }

    def query(self, key: str) -> str:
        return self.data.get(key, "Information not found in the text database.")

class ResponseGenerator:
    @staticmethod
    def generate(query: str, context: str) -> str:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        response = llm.invoke(prompt)
        return response.content

class PostgreSQLDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        self.conn.autocommit = True  # This will commit each query automatically

    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()

class ChatBot:
    def __init__(self, vector_store: FAISS, postgres_db: PostgreSQLDatabase):
        self.vector_store = vector_store
        self.postgres_db = postgres_db
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=GOOGLE_API_KEY)
        self.pdf_summary = self.generate_pdf_summary()
        self.db_structure = self.analyze_database()

    def generate_pdf_summary(self) -> str:
        docs = VectorStore.query(self.vector_store, "Summarize the entire content", k=10)
        chain = load_summarize_chain(self.llm, chain_type="map_reduce")
        summary = chain.run(docs)
        return summary

    def analyze_database(self) -> str:
        try:
            # Get list of tables
            tables = self.postgres_db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            
            structure = []
            for table in tables:
                table_name = table['table_name']
                # Get columns for each table
                columns = self.postgres_db.query(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
                structure.append(f"Table: {table_name}")
                structure.append("Columns:")
                for column in columns:
                    structure.append(f"  - {column['column_name']} ({column['data_type']})")
                
                # Get a sample of data from each table
                sample_data = self.postgres_db.query(f"SELECT * FROM {table_name} LIMIT 1")
                if sample_data:
                    structure.append("Sample data:")
                    structure.append(str(sample_data[0]))
                
                structure.append("")  # Empty line for readability
            
            return "\n".join(structure)
        except Exception as e:
            return f"Error analyzing database structure: {str(e)}"

    def decide_source(self, query: str) -> str:
        prompt = f"""Given the following query, a summary of PDF contents, and a description of the database structure, decide which data source would be most appropriate to answer it:

        Query: {query}

        PDF Summary: {self.pdf_summary}

        Database Structure:
        {self.db_structure}

        Options:
        1. PDF documents
        2. PostgreSQL database

        Respond with only the number of the most appropriate option."""

        response = self.llm.invoke(prompt)
        print("decide_source",response.content)
        return response.content.strip()

    def get_response(self, query: str) -> str:
        source = self.decide_source(query)
        
        if source == "1":
            return self.get_pdf_specific_response(query)
        elif source == "2":
            return self.get_postgres_response(query)
        else:
            return "I'm not sure which data source to use for this query."

    def get_pdf_specific_response(self, query: str) -> str:
        relevant_docs = VectorStore.query(self.vector_store, query)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        prompt = f"Context from PDF documents:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        response = self.llm.invoke(prompt)
        return response.content

    def get_postgres_response(self, query: str) -> str:
        prompt = f"""Given the following user query, generate an appropriate SQL query to retrieve the relevant information from a PostgreSQL database:
        User Query: {query}
        
        Database Structure:
        {self.db_structure}
        
        Respond with only the SQL query, without any additional text, explanation, or formatting symbols."""

        sql_query = self.llm.invoke(prompt).content.strip()
        
        # Remove any markdown formatting
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        try:
            print(f"Executing SQL query: {sql_query}")  # Debug print
            results = self.postgres_db.query(sql_query)
            print(f"Query results: {results}")  # Debug print
            if not results:
                return f"No results found for this query in the database. The executed SQL query was: {sql_query}"
            
            # Format the results into a more readable string
            formatted_results = "\n".join([f"{key}: {value}" for row in results for key, value in row.items()])
            
            answer_prompt = f"""Based on the following database query results, answer the user's question:

            User Question: {query}

            Query Results:
            {formatted_results}

            Provide a concise and accurate answer based on these results."""

            response = self.llm.invoke(answer_prompt)
            return response.content
        except Exception as e:
            return f"An error occurred while querying the database: {str(e)}\nThe generated SQL query was: {sql_query}"

    def chat_loop(self):
        print("Chat with your AI assistant! (Type 'exit' to quit, or press Enter to use speech input)")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            elif user_input == '':
                print("Speak your query...")
                query = speech_to_text()
                if not query:
                    print("Sorry, I couldn't understand that. Please try again.")
                    continue
                print(f"You said: {query}")
            else:
                query = user_input
            
            try:
                response = self.get_response(query)
                print("AI:", response)
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    try:
        # Load and process documents
        documents = PDFLoader.load_pdfs(PDF_PATHS)
        if not documents:
            raise ValueError("No documents were loaded. Please check your PDF paths and file permissions.")
        
        split_docs = DocumentSplitter.split_documents(documents)
        
        # Create vector store
        vector_store = VectorStore.create(split_docs)
        
        # Create PostgreSQL database connection
        postgres_db = PostgreSQLDatabase()
        
        # Start chat bot
        chat_bot = ChatBot(vector_store, postgres_db)
        chat_bot.chat_loop()
    except Exception as e:
        print(f"An error occurred during setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'postgres_db' in locals():
            postgres_db.close()

if __name__ == "__main__":
    main()
