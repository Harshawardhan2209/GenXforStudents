import streamlit as st
import json

from streamlit_lottie import st_lottie 

st.text_area('Point 1', "Summerize in 50 words [Topic]")

st.text_area('Point 2',"Tell me about given context")

st.text_area('Point 3', "make 10 quetions with answers Based on given Context")


st.write("Keep Learning, keep exploring")

with open('src/ATS.json') as anim_source:
    animation = json.load(anim_source)
st_lottie(animation, 1, True, True, "high", 200, -200)