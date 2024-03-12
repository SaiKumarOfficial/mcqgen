import json
import os
import traceback
import pandas as pd 
from dotenv import load_dotenv
from src.mcqgenerator.utils import get_table_data
import streamlit as st                
from langchain_community.callbacks import get_openai_callback
from src.mcqgenerator.MCQgenerator import generate_chain
from src.mcqgenerator.logger import logging

if not os.path.exists("uploads"):
    os.makedirs("uploads")

with open("response.json","r") as file:
    RESPONSE_JSON = json.load(file)

def save_uploaded_file(uploaded_file):
    with open(os.path.join("uploads", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.join("uploads", uploaded_file.name)

# creating a title for app
st.title("MCQs Creator Application with PaLM and Langchain")

# create a form using st.form
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or txt file")
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            file_path = save_uploaded_file(uploaded_file)
            st.success(f"File uploaded successfully: {uploaded_file.name}")
            st.write("Content of the uploaded file:")
            with open(file_path, "r") as f:
                file_content = f.read()
                st.write(file_content)
        else:
            st.error("Unsupported file format. Please upload a .txt file.")

    mcq_count = st.number_input("No.of MCQs", min_value=5, max_value=50)

    subject = st.text_input("Enter Subject", max_chars=20)

    tone = st.text_input("Complexity level of questins", max_chars=20, placeholder="Simple")

    button = st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Loading......."):
            try:
                
                
                with get_openai_callback() as cb:
                    # generate_evaluate_chain = generate_chain()
                    response=generate_chain(file_content,mcq_count,subject,tone,RESPONSE_JSON)
                        
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")
            
            else:
                # print(f"Total tokens:{cb.total_tokens}")
                # print(f"Promt Tokens: {cb.prompt_tokens}")
                # print(f"Completiom Tokens: {cb.completion_tokens}")
                # print(f"Total Cost: {cb.total_cost}")

                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.text_area(label="Review", value=response["review"])
                            st.write(df)
                        else:
                            st.error("Error in the table data")
                    else:
                        st.write(response)


                



