import streamlit as st
from web_scrap import course_links
from main import generate_embeddings_from_web,generate_embeddings_from_excel,generate_response
st.title("AV Search")

if "links" not in st.session_state:
    with st.spinner('Getting course URLs'):
        base_url = "https://courses.analyticsvidhya.com/collections/courses?page="
        st.session_state.links = course_links(base_url)
    st.success('Got all course URLs')

if "db_web" not in st.session_state:
    with st.spinner('Generating Web Embeddings, this might take a few minutes.'):
        st.session_state.db_web = generate_embeddings_from_web(st.session_state.links)
    st.success('Generated Web Embeddings.')
if "db_excel" not in st.session_state:
    with st.spinner('Generating Data Embeddings, this might take a few minutes.'):
        st.session_state.db_excel = generate_embeddings_from_excel()
    st.success('Generated Data Embeddings. Please ask your queries now. Thank you for waiting.')



# Input for user query
query = st.text_input("Enter your query:")

if st.button("Search"):
    response = generate_response(st.session_state.db_web, st.session_state.db_excel , query)
    if response:
        st.markdown(response)



