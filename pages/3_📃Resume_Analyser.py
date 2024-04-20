import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_lottie import st_lottie 
import json
import pickle

load_dotenv()

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))



def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    with open("ResumeAnz.pkl", "wb") as f:
        pickle.dump(vector_store, f)

def get_conversational_chain():
    prompt_template = """
    You are an Advance resume Analyzer.
    1. analyse the resume and give the best 3 Job Domain relavent to skills in given context.
    2. based on that job domains seprately suggest more skill and best cources from youtube.
    3. Suggest the improvememnt in resume.
    4. Use bullet points, tables and keep text more interactive
    5. make sure that the provide youtube links are working and are latest.
    
    Context:\n {context}?\n


    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    with open("ResumeAnz.pkl", "rb") as f:
        new_db = pickle.load(f)
    
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs},
        return_only_outputs=True
    )

    st.session_state.output_text = response["output_text"]
    st.write("Reply: ", st.session_state.output_text)

def main():
    
    with open('src/Resume.json', encoding='utf-8') as anim_source:
        animation = json.load(anim_source)
    st_lottie(animation, 1, True, True, "high", 200, -200)


    
    st.header("Resume Analyser")

    if 'pdf_docs' not in st.session_state:
        st.session_state.pdf_docs = None

    if 'output_text' not in st.session_state:
        st.session_state.output_text = ""

    if 'prompt_selected' not in st.session_state:
        st.session_state.prompt_selected = ""

    pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)

    if st.button("Process"):
        if pdf_docs:
            with st.spinner("Analysing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                user_input(raw_text)  # Call user_input function with raw_text


        #Additional Courses
        st.divider()
        st.text("Additional Courses: ")
        st.video('https://www.youtube.com/watch?v=JxgmHe2NyeY&t')
        st.divider()
        st.video('https://www.youtube.com/watch?v=5NQjLBuNL0I')
        st.divider()


    
        
    if pdf_docs:
        st.session_state.pdf_docs = pdf_docs

if __name__ == "__main__":
    main()





