import pandas as pd
import streamlit as st
import random
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("")

# initialize session state
if "press_list" not in st.session_state:
	st.session_state.press_list = random.sample(["P"] * 3 + ["N"] * 3, 6)
if "results" not in st.session_state:
	st.session_state.results = [None] * 6
if "started" not in st.session_state:
	st.session_state.started = False
if "finished" not in st.session_state:
	st.session_state.finished = False
if "stage" not in st.session_state:
	st.session_state.stage = 1

# layout: centered column
_, center, _ = st.columns([1, 2, 1])

with center:
	# briefing shown only before start
	if not st.session_state.started:
		st.markdown("""
- This test aims to check if the call bell works every time it should, and takes **1 minute**.
- Please get ready to follow the instructions at each stage!
""")

	# Start button (hidden after clicked)
	if not st.session_state.started and not st.session_state.finished:
		if st.button("Start Test", use_container_width=True):
			st.session_state.started = True
			st.session_state.stage = 1
			st.experimental_rerun()  # <- ensures briefing and button disappear immediately

	# Active stage display (advances only when Next pressed)
	if st.session_state.started and not st.session_state.finished:
		i = st.session_state.stage
		label = st.session_state.press_list[i - 1]

		st.markdown(f"## Stage {i}/6")
		if label == "P":
			st.warning("Ask the patient to **activate the bell** now.")
		else:
			st.warning("Ask the patient to **lie down, then sit back up naturally** now.")

		# radio with no default selection
		choice = st.radio(
			"Select either **T** or **F**:",
			["T", "F"],
			index=None,
			horizontal=True,
			key=f"trial_{i}",
		)

		# Next button disabled until a choice is made
		col1, col2, col3 = st.columns([1, 1, 1])
		with col2:
			if st.session_state.stage < 6:
				if st.button("Next", use_container_width=True, disabled=(choice not in ("T", "F"))):
					st.session_state.results[i - 1] = choice
					st.session_state.stage += 1
					st.experimental_rerun()
			else:
				# final step: Finish button
				if st.button("Finish", use_container_width=True, disabled=(choice not in ("T", "F"))):
					st.session_state.results[i - 1] = choice
					st.session_state.finished = True
					st.session_state.started = False
					st.experimental_rerun()

		st.caption("Advance when ready. Each stage is quick.")

	# Finished: show mutually exclusive outcome and downloads
	if st.session_state.finished:
		complete = all(r in ("T", "F") for r in st.session_state.results)
		if not complete:
			st.error("The test failed: at least one stage is missing a result. Please run the test again.")
		else:
			st.success("The test is complete. Download the results below.")

			df = pd.DataFrame(
				{"Press List": st.session_state.press_list, "Activated?": st.session_state.results},
				index=[1, 2, 3, 4, 5, 6],
			)

			# timestamped filename prefix (HHMM)
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
