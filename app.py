import streamlit as st
import spacy
import fitz
from annotated_text import annotated_text


@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    french_model = spacy.load("./models/fr/")
    english_model = spacy.load("./models/en/")
    models = {"en": english_model, "fr": french_model}
    return models


def process_text(doc, selected_entities, anonymize=False):
    tokens = []
    for token in doc:
        if (token.ent_type_ == "PERSON") & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda"))
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        else:
            tokens.append(" " + token.text + " ")

    if anonymize:
        anonmized_tokens = []
        for token in tokens:
            if type(token) == tuple:
                anonmized_tokens.append(("X" * len(token[0]), token[1], token[2]))
            else:
                anonmized_tokens.append(token)
        return anonmized_tokens

    return tokens


models = load_models()

selected_language = st.sidebar.selectbox("Select a language", options=["en", "fr"])
selected_entities = st.sidebar.multiselect(
    "Select the entities you want to detect",
    options=["LOC", "PER", "ORG"],
    default=["LOC", "PER", "ORG"],
)
selected_model = models[selected_language]

text_input = st.text_area("Type a text to Analyze")

uploaded_file = st.file_uploader("or Upload a file", type=[  "pdf" ])
if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    print( "filename:", uploaded_file.name)    
    st.write("filename:", uploaded_file.name)
    pathlocalfichero= uploaded_file.name
    open(pathlocalfichero , 'wb').write(bytes_data)    
    st.write(pathlocalfichero)
    pdf = fitz.open(pathlocalfichero)
    pages = list(range(pdf.pageCount))
    textoblock=""
    for pg in range(pdf.pageCount):
        page = pdf[pg]
        texto=page.get_text()
        textoblock=textoblock+texto
    #text_input = text_input.decode("utf-8")
    st.write(textoblock)    
    
anonymize = st.button("Analyze")
doc = selected_model(text_input)
tokens = process_text(doc, selected_entities)

annotated_text(*tokens)

if anonymize:
    st.markdown("**Analized text**")
    st.markdown("---")
    anonymized_tokens = process_text(doc, selected_entities, anonymize=anonymize)
    annotated_text(*anonymized_tokens)
