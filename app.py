import streamlit as st
import tempfile

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from pathlib import Path
from pypdf import PdfReader

load_dotenv()  # Betölti a .env fájlból az API kulcsot

def get_response(chat_history, model):
    response = model.invoke(chat_history)
    return response.content

def extract(input_file, type):
    if type == 'pdf':
        extracted_text = ""
        reader = PdfReader(input_file)
        pages = reader.pages

        for page in pages:
            extracted_text += page.extract_text()

        return extracted_text

    if type == 'txt':
        with open(input_file, "r") as file:
            return file.read()

st.header("Üdvözöllek, én vagyok a személyes jogászod!")
st.write("**Tegyél fel bármilyen jogi kérdést vagy adj konkrét jogi dokumentumok!**")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content=extract('first_prompt.txt', 'txt'))
    ]

if "model" not in st.session_state:
    st.session_state.model = ChatGroq(model='llama-3.3-70b-versatile')

# Előző üzenetek kirajzolása (SystemMessage-t kihagyjuk)
for msg in st.session_state.chat_history[1:]:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    st.chat_message(role).write(msg.content)

# Input
file = st.file_uploader("")

if file:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name  # os.PathLike


user_input = st.chat_input("")

if user_input:
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)

    response = get_response(st.session_state.chat_history, st.session_state.model)
    st.session_state.chat_history.append(AIMessage(content=response))
    st.chat_message("assistant").write(response)

if file is not None:
    path = Path(tmp_path)
    if path.is_file():
        content = extract(file, 'pdf')
        st.session_state.chat_history.append(HumanMessage(content=content))
        st.chat_message("user").write(f"📄 Fájl feltöltve")

    response = get_response(st.session_state.chat_history, st.session_state.model)
    st.session_state.chat_history.append(AIMessage(content=response))
    st.chat_message("assistant").write(response)