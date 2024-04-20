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
    with open("faiss_index.pkl", "wb") as f:
        pickle.dump(vector_store, f)

def get_conversational_chain():
    prompt_template = """
    Leave First 1 line empty and then give reply
    1. Answer the question as detailed as possible from the provided context 
    2. (if not in context search on Internet), 
    3. make sure to provide all the details Properly, 
    4. use pointers and tables to make context more readable. 
    5. If information not found then search on google and then provide reply.
    6. (but then mention the reference name)
    7. If 'Summarize' word is used in input then Summarize the context.
    8. If input is: 'Hello', reply: Hey hi buddy.\n\n
    9. Use Markdown font to make text more readable
    
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    with open("faiss_index.pkl", "rb") as f:
        new_db = pickle.load(f)
    
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )

    st.session_state.output_text = response["output_text"]
    st.write("Reply: ", st.session_state.output_text)

def main():
    st.set_page_config("College.ai", page_icon='🔍', layout='centered')
    st.header("Ask_to_PDF- Start chat")

    if 'pdf_docs' not in st.session_state:
        st.session_state.pdf_docs = None

    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""

    if 'output_text' not in st.session_state:
        st.session_state.output_text = ""

    if 'prompt_selected' not in st.session_state:
        st.session_state.prompt_selected = ""

    pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)

    if st.button("Train & Process"):
        if pdf_docs:
            with st.spinner("🤖Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done, AI is trained")

    with open('src/Robot.json', encoding='utf-8') as anim_source:
        animation = json.load(anim_source)
    st_lottie(animation, 1, True, True, "high", 100, -200)

    #st.text("______________If <AI is trained>, then only write your queries._______________")
    user_question = st.text_input("Ask a Question from the PDF Files")
    enter_button = st.button('Enter')

    if enter_button or st.session_state.prompt_selected:
        if st.session_state.prompt_selected:
            user_question = st.session_state.prompt_selected
            st.session_state.prompt_selected = ""
        if st.session_state.user_question != user_question:
            st.session_state.user_question = user_question
            st.session_state.output_text = ""  # Reset output text when input changes

        if user_question:
            user_input(user_question)

    if pdf_docs:
        st.session_state.pdf_docs = pdf_docs

    

if __name__ == "__main__":
    main()
