import pandas as pd
import streamlit as st
import random, time
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("")

if "press_list" not in st.session_state:
	st.session_state.press_list = random.sample(["P"] * 3 + ["N"] * 3, 6)
if "results" not in st.session_state:
	st.session_state.results = [None] * 6
if "finished" not in st.session_state:
	st.session_state.finished = False
if "started" not in st.session_state:
	st.session_state.started = False

_, center, _ = st.columns([1, 2, 1])

with center:
	if not st.session_state.started:
		st.markdown("""
- This test aims to check if the call bell works every time it should, and takes **1 minute**.
- Please get ready to follow the instructions at each stage!
""")

	if not st.session_state.finished and st.button("Start Test", use_container_width=True):
		st.session_state.started = True
		placeholder = center.empty()
		for i, label in enumerate(st.session_state.press_list, 1):
			with placeholder.container():
				st.markdown(f"## Stage {i}/6")
				if label == "P":
					st.warning("Ask the patient to **activate the bell** now.")
				else:
					st.warning("Ask the patient to **lie down, then sit back up naturally** now.")
				st.session_state.results[i - 1] = st.radio(
					"Select **T** if the bell activated, and **F** otherwise:",
					["T", "F"],
					horizontal=True,
					index=None,
					key=f"trial_{i}",
				)
				st.caption("Showing the next step in 10 seconds.")
			time.sleep(10)
		placeholder.empty()
		st.session_state.finished = True
		st.success("The test is complete! Please download the results below.")

	if st.session_state.finished:
		if any(r not in ("T", "F") for r in st.session_state.results):
			st.error("The test failed: at least one step is missing a result. Please try again.")
		else:
			df = pd.DataFrame(
				{"Press List": st.session_state.press_list, "Activated?": st.session_state.results},
				index=[1, 2, 3, 4, 5, 6],
			)

			# Generate timestamped filename prefix (HHMM)
			now = datetime.now().strftime("%H%M")
			filename_base = f"{now}-ucb-test-1"

			# CSV
			csv_buffer = BytesIO()
			df.to_csv(csv_buffer, index=True)
			st.download_button(
				label="📥 Download as CSV",
				data=csv_buffer.getvalue(),
				file_name=f"{filename_base}.csv",
				mime="text/csv",
				use_container_width=True,
			)

			# PDF
			pdf = FPDF()
			pdf.add_page()
			pdf.set_font("Arial", "B", 14)
			pdf.cell(0, 10, "Universal Call Bell - Test 1 Results", ln=True, align="C")
			pdf.ln(10)
			pdf.set_font("Arial", "", 12)
			pdf.cell(30, 10, "Index", 1, 0, "C")
			pdf.cell(60, 10, "Press List", 1, 0, "C")
			pdf.cell(60, 10, "Activated?", 1, 1, "C")
			for i in range(6):
				pdf.cell(30, 10, str(i + 1), 1, 0, "C")
				pdf.cell(60, 10, str(df.iloc[i, 0]), 1, 0, "C")
				pdf.cell(60, 10, str(df.iloc[i, 1]), 1, 1, "C")
			pdf_bytes = pdf.output(dest="S")
			st.download_button(
				label="📥 Download as PDF",
				data=pdf_bytes,
				file_name=f"{filename_base}.pdf",
				mime="application/pdf",
				use_container_width=True,
			)

			st.dataframe(df, use_container_width=True)
