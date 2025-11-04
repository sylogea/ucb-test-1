import pandas as pd
import streamlit as st
import random, time
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("")

if "press_list" not in st.session_state:
	st.session_state.press_list = random.sample(["P"] * 3 + ["N"] * 3, 6)
if "results" not in st.session_state:
	st.session_state.results = [None] * 6
if "started" not in st.session_state:
	st.session_state.started = False
if "finished" not in st.session_state:
	st.session_state.finished = False
if "start_time" not in st.session_state:
	st.session_state.start_time = None

_, center, _ = st.columns([1, 2, 1])

with center:
	brief = st.empty()
	if not st.session_state.started:
		with brief.container():
			st.markdown("""
- This test aims to check if the call bell works every time it should, and takes **1 minute**.
- Please get ready to follow the instructions at each stage!
""")

	if not st.session_state.started and not st.session_state.finished:
		if st.button("Start Test", use_container_width=True):
			st.session_state.started = True
			st.session_state.start_time = time.time()
			brief.empty()
			st.experimental_rerun()

	# live step display driven by elapsed time
	if st.session_state.started and not st.session_state.finished:
		elapsed = time.time() - st.session_state.start_time
		step = int(elapsed // 10) + 1
		if step > 6:
			st.session_state.finished = True
			st.experimental_rerun()

		label = st.session_state.press_list[step - 1]
		placeholder = st.empty()
		with placeholder.container():
			st.markdown(f"## Stage {step}/6")
			if label == "P":
				st.warning("Ask the patient to **activate the bell** now.")
			else:
				st.warning("Ask the patient to **lie down, then sit back up naturally** now.")
			# radio with no default selection
			st.session_state.results[step - 1] = st.radio(
				"Select either **T** or **F**:",
				["T", "F"],
				horizontal=True,
				index=None,
				key=f"trial_{step}",
			)
			remaining = 10 - int(elapsed % 10)
			st.caption(f"Showing the next step in {remaining} seconds.")
		time.sleep(1)
		st.experimental_rerun()

	# finished: mutually exclusive outcomes
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
