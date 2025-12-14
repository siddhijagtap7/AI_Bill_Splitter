import os
import google.generativeai as genai
import pandas as pd
import json
from functools import lru_cache
import streamlit as st
from config import config

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)


@lru_cache
def load_model():
    model = genai.GenerativeModel(
        'models/gemini-2.5-flash'
    )
    return model

def items_price(text):
    """
        Extracts item names, quantities, and prices from the given text using a generative AI model.
        Args:
            text (str): The text extracted from the bill image.
            Returns:
            pd.DataFrame: A DataFrame containing 'Items', 'Quantity', and 'Prices' columns.
    """
    # prompt = f"""
    # You are an AI assistant. Here is a restaurant bill. Understand the bill and your task is to create a json string of item, quantity and price only from the below given data. For prices, only the price should be as the output, not any symbol preceeding or succeeding it.
    # Data: {text}

    # """
    # prompt = prompt + """
    # Expected Output Format: If the data contains three items,
    #     {
    #     "Items": ["Item1","Item2","Item3"],
    #     "Quantity": ["Quantity1","Quantity2","Quantity3"],
    #     "Prices": ["Price1","Price2","Price3"]
    #     }"""
    prompt = config.items_price_prompt.format(text=text)
    model = load_model()
    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(
                temperature=0.1,candidate_count=1)
                )
    response = response.text
    cleaned_string = response.strip("```json\n").strip("```")
    data = json.loads(cleaned_string)
    df = pd.DataFrame(data)
    df['Prices'] = df['Prices'].astype(float)
    return df

def total_gst(text):
    """
        Extracts total amount, CGST percentage, and SGST percentage from the given text using a generative AI model.
        Args:
            text (str): The text extracted from the bill image.
            Returns:
            pd.DataFrame: A DataFrame containing 'Total', 'CGST', and 'SGST' columns.
    """
    # prompt2 = f"""
    # You are an AI assistant. Here is a restaurant bill. Understand the bill and your task is to create a json string of final total amount, cgst percentage, sgst percentage only from the below given data. Extract percentage not the amount. If no SGST or CGST is present, consider 0. Ensure that the total amount is the final total inclusive of all taxes. The percentaage symbol should np=ot be present. The response given would be directly loaded into json, so give it accordingly; no backticks
    # Data: {text}

    # """
    # prompt2 = prompt2 + """
    # Expected Output Format: 
    #     {
    #     "Total": "",
    #     "CGST": "",
    #     "SGST": ""
    #     }"""
    model = load_model()
    prompt = config.tax_total_prompt.format(text=text)
    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(
                temperature=0.1,candidate_count=1)
                )
    data = json.loads(response.text)
    df = pd.DataFrame([data])
    df = df.astype(float)
    return df