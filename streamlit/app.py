import streamlit as st
import pandas as pd
import numpy as np
import time

st.text("Fixed width text")
st.markdown("_Markdown_")
st.latex(r""" e^{i\pi} + 1 = 0 """)
st.title("My title")
st.header("My header")
st.subheader("My sub")
st.code("for i in range(8): foo()")
st.badge("New")
st.html("<p>Hi!</p>")

df = pd.DataFrame({'col1': range(20), 'col2': reversed(range(20))})

st.dataframe(df)
st.table(df.iloc[0:10])
st.json({"foo":"bar","fu":"ba"})
st.metric("My metric", 42, 2)

data = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
)

st.button("Click me")
st.download_button(label="Download file", data=data.to_csv().encode(), file_name= 'data.csv', mime='text/csv')
st.link_button("Go to gallery", "https://naver.com")
st.page_link("https://google.com", label="Home")
st.data_editor(data)
st.checkbox("I agree")
st.feedback("thumbs")
st.pills("Tags", ["Sports", "Politics"])
st.radio("Pick one", ["cats", "dogs"])
st.segmented_control("Filter", ["Open", "Closed"])
st.toggle("Enable")
st.selectbox("Pick one", ["cats", "dogs"])
st.multiselect("Buy", ["milk", "apples", "potatoes"])
st.slider("Pick a number", 0, 100)
st.select_slider("Pick a size", ["S", "M", "L"])
st.text_input("First name")
st.number_input("Pick a number", 0, 10)
st.text_area("Text to translate")
st.date_input("Your birthday")
st.time_input("Meeting time")
st.file_uploader("Upload a CSV")
st.audio_input("Record a voice message")
st.camera_input("Take a picture")
st.color_picker("Pick a color")

def foo():
    st.write('foo')

def b():
    st.write('b')

# Use widgets' returned values in variables:
for i in range(int(st.number_input("Num:"))):
    foo()
if st.sidebar.selectbox("I:",["f"]) == "f":
    b()
my_slider_val = st.slider("Quinn Mallory", 1, 88)
st.write(my_slider_val)

# Disable widgets to remove interactivity:
# st.slider("Pick a number", 0, 100, disabled=True)    

st.image("https://static.streamlit.io/examples/cat.jpg")
# st.audio(data)
# st.video(data)
# st.video(data, subtitles="./subs.vtt")
# st.logo("logo.jpg")

# Insert a chat message container.
with st.chat_message("user"):
    st.write("Hello 👋")
    st.line_chart(np.random.randn(30, 3))

# Display a chat input widget at the bottom of the app.
st.chat_input("Say something")

# Group multiple widgets:
with st.form(key="my_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type= 'password')
    st.form_submit_button("Login")

# Show a spinner during a process
with st.spinner(text="In progress"):
    time.sleep(3)
    st.success("Done")

# Show and update progress bar
bar = st.progress(50)
time.sleep(3)
bar.progress(100)

with st.status("Authenticating...") as s:
    time.sleep(2)
    st.write("Some long response.")
    s.update(label="Response")

st.balloons()
st.snow()
st.toast("Warming up...")
st.error("Error message")
st.warning("Warning message")
st.info("Info message")
st.success("Success message")
st.exception(Exception())