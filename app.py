import streamlit as st
import random
import time

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("🔔 Universal Call Bell - Test 1")

if "press_list" not in st.session_state:
	st.session_state.press_list = []

if st.button("Generate List"):
	L = random.sample(["P"] * 3 + ["N"] * 3, 6)
	st.session_state.press_list = L
	st.write("### Generated List")
	st.table({"Press List": L})

if st.session_state.press_list and st.button("Start Experiment"):
	st.write("### Running Experiment (1 minute total)")
	for i, label in enumerate(st.session_state.press_list, 1):
		st.markdown(f"## Step {i}/6")
		if label == "P":
			st.info("Tell the patient to **press the call button now.**")
		else:
			st.warning("Tell the patient to **perform a natural non-press action.**")
		st.caption("Next instruction in 10 seconds...")
		time.sleep(10)
	st.success("Experiment finished.")
