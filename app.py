import pandas as pd
import streamlit as st
import random
from fpdf import FPDF
from io import BytesIO

def _rerun():
	fn = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
	if callable(fn):
		fn()

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("")

if "should_activate" not in st.session_state:
	st.session_state.should_activate = random.sample(["T"] * 3 + ["F"] * 3, 6)
if "results" not in st.session_state:
	st.session_state.results = [None] * 6
if "started" not in st.session_state:
	st.session_state.started = False
if "finished" not in st.session_state:
	st.session_state.finished = False
if "stage" not in st.session_state:
	st.session_state.stage = 1
if "patient_name" not in st.session_state:
	st.session_state.patient_name = ""

_, center, _ = st.columns([1, 2, 1])

with center:
	if (not st.session_state.started) and (not st.session_state.finished):
		st.markdown("This test aims to check if the call bell works every time it should, and takes **1 minute**. Get ready to follow the instructions at each stage!")
		st.session_state.patient_name = st.text_input("Enter a name for the patient...")

	if (not st.session_state.started) and (not st.session_state.finished):
		if st.button("Start Test", use_container_width=True, disabled=not st.session_state.patient_name.strip()):
			st.session_state.started = True
			st.session_state.stage = 1
			_rerun()

	if st.session_state.started and (not st.session_state.finished):
		i = st.session_state.stage
		label = st.session_state.should_activate[i - 1]

		st.markdown(f"## Stage {i}/6")
		if label == "T":
			st.warning("Ask the patient to **activate the bell** now.")
		else:
			st.warning("Ask the patient to **lie down, then sit back up naturally** now.")

		choice = st.radio(
			"Select **T** if the bell activated, and **F** otherwise:",
			["T", "F"],
			index=None,
			horizontal=True,
			key=f"trial_{i}",
		)

		col1, col2, col3 = st.columns([1, 1, 1])
		with col2:
			if st.session_state.stage < 6:
				if st.button("Next", use_container_width=True, disabled=(choice not in ("T", "F"))):
					st.session_state.results[i - 1] = choice
					st.session_state.stage += 1
					_rerun()
			else:
				if st.button("Finish", use_container_width=True, disabled=(choice not in ("T", "F"))):
					st.session_state.results[i - 1] = choice
					st.session_state.finished = True
					st.session_state.started = False
					_rerun()

	if st.session_state.finished:
		complete = all(r in ("T", "F") for r in st.session_state.results)
		if not complete:
			st.error("The test failed: at least one stage is missing a result. Please try again.")
		else:
			st.success("The test is complete. Please download the results.")

			df = pd.DataFrame(
				{"Should Activate?": st.session_state.should_activate, "Activated?": st.session_state.results},
				index=[1, 2, 3, 4, 5, 6],
			)

			filename_base = "ucb-test-1"

			csv_buffer = BytesIO()
			df.to_csv(csv_buffer, index=True)

			pdf = FPDF()
			pdf.add_page()
			pdf.set_font("Arial", "", 12)
			pdf.cell(30, 10, "Index", 1, 0, "C")
			pdf.cell(60, 10, "Should Activate?", 1, 0, "C")
			pdf.cell(60, 10, "Activated?", 1, 1, "C")
			for i in range(6):
				pdf.cell(30, 10, str(i + 1), 1, 0, "C")
				pdf.cell(60, 10, str(df.iloc[i, 0]), 1, 0, "C")
				pdf.cell(60, 10, str(df.iloc[i, 1]), 1, 1, "C")

			out = pdf.output(dest="S")
			pdf_bytes = out.encode("latin-1") if isinstance(out, str) else bytes(out)

			col1, col2 = st.columns(2)
			with col1:
				st.download_button(
					label="📥 Download CSV",
					data=csv_buffer.getvalue(),
					file_name=f"{filename_base}.csv",
					mime="text/csv",
					use_container_width=True,
				)
			with col2:
				st.download_button(
					label="📥 Download PDF",
					data=pdf_bytes,
					file_name=f"{filename_base}.pdf",
					mime="application/pdf",
					use_container_width=True,
				)

			st.dataframe(df, use_container_width=True)
