import streamlit as st
from PIL import Image
from core.extract import img_to_text
import core.model as m
from core.dataframe import get_individual_prices
import pandas as pd
import pytesseract
import os
from config import config

logo = Image.open("assets/logo.png")
st.set_page_config(page_title="Bill Splitter", page_icon=logo)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Hides the hamburger menu */
    footer {visibility: hidden;}    /* Hides the footer */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if os.path.exists("/usr/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = config.docker_tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = config.local_tesseract_path


col1, col2 = st.columns([0.8, 4])

with col1:
    st.image(logo, width=90)  

with col2:
    st.title("Bill Splitter")

n = st.text_input("Enter the number of people:")
if n.isdigit() and int(n) > 0:
    n = int(n)
else:
    st.error("Please enter a valid number of people.")
    st.stop()

uploaded_file = st.file_uploader("Upload the bill", type=["jpg", "jpeg", "png"])

@st.cache_data
def process_image(file):
    """Extract data from the uploaded image and process it."""
    text = img_to_text(file)
    df_items = m.items_price(text)
    df_price = m.total_gst(text)
    return df_items, df_price



if uploaded_file is not None:
    with st.expander("View Uploaded Bill", expanded=False):
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

    if "ocr_done" not in st.session_state:
        df_items, df_price = process_image(uploaded_file)
        st.session_state.df_items = df_items.copy()
        st.session_state.df_price = df_price.copy()
        st.session_state.ocr_done = True
    
    rows = st.session_state.df_items.shape[0]


    # initialize session state variables
    if "selections" not in st.session_state:
        st.session_state.selections = [[0] * n for _ in range(rows)]
    if "df_items" not in st.session_state:
        st.session_state.df_items = df_items.copy()
    if "df_price" not in st.session_state:
        st.session_state.df_price = df_price.copy()
    if "split_results" not in st.session_state:
        st.session_state.split_results = None

    st.write("Select options from the grid and enter your input below:")

    for i in range(rows):
        st.write(f"**{st.session_state.df_items['Items'][i]}**")
        cols = st.columns(n)

        for j in range(n):
            with cols[j]:
                key = f"chk-{i}-{j}"
                checked = st.checkbox(f"Person {j+1}", key=key)
                st.session_state.selections[i][j] = int(checked)


    with st.expander("View or Edit Items and Prices", expanded=False):
        st.write("Items and Prices:")
        st.session_state.df_items = st.data_editor(st.session_state.df_items, key="df_items_editor")
        st.write("Price Breakdown with GST:")
        st.session_state.df_price = st.data_editor(st.session_state.df_price, key="df_price_editor")
        
    new_rows = st.session_state.df_items.shape[0]

    if len(st.session_state.selections) != new_rows:
        st.session_state.selections = [[0] * n for _ in range(new_rows)]
    if st.button("Split"):
        # use the updated session state values
        mat = st.session_state.selections
        df_items = st.session_state.df_items
        df_price = st.session_state.df_price
        amt = get_individual_prices(mat, df_items, df_price)
        # print(amt)
        # print(df_items)
        # print(df_price)
        
        # generate split results and store in session state
        split_mat = []
        for i in range(n):
            total = amt[i].sum()
            split_mat.append([f'Person {i+1}', total])
        split_mat = pd.DataFrame(split_mat, columns=["Person", "Amount"])
        st.session_state.split_results = split_mat

    if st.session_state.split_results is not None:
        st.write("Amount to be paid:")
        st.write(st.session_state.split_results)

