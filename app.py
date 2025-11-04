import streamlit as st
import random

st.set_page_config(page_title="Call Bell Test", page_icon="🔔", layout="centered")

st.title("🔔 Call Bell Reliability Test")

if "press_list" not in st.session_state:
	st.session_state.press_list = []
if "results" not in st.session_state:
	st.session_state.results = []

if st.button("Generate List"):
	st.session_state.press_list = random.sample(["P"] * 3 + ["N"] * 2, 5)
	st.session_state.results = []

if st.session_state.press_list and st.button("Start Experiment"):
	for i, label in enumerate(st.session_state.press_list, 1):
		st.markdown(f"### Step {i}/5")
		if label == "P":
			st.info("Tell the patient to **press the call button once now.**")
		else:
			st.warning("Tell the patient to **lie down and sit back up naturally.**")

		st.session_state.results.append(
			st.radio(f"Trial {i}: Did the alert activate within 20 s?", ["T", "F"], horizontal=True)
		)
		st.write("---")

	if len(st.session_state.results) == 5:
		Ps, Rs = st.session_state.press_list, st.session_state.results
		TP = sum(l == "P" and r == "T" for l, r in zip(Ps, Rs))
		FN = sum(l == "P" and r == "F" for l, r in zip(Ps, Rs))
		FP = sum(l == "N" and r == "T" for l, r in zip(Ps, Rs))
		TN = sum(l == "N" and r == "F" for l, r in zip(Ps, Rs))
		TPR = TP / (TP + FN) if TP + FN else 0
		FPR = FP / (FP + TN) if FP + TN else 0

		st.metric("True Positive Rate", f"{TPR:.2f}")
		st.metric("False Positive Rate", f"{FPR:.2f}")
