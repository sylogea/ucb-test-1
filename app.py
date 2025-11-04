import streamlit as st
import random
import time
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Universal Call Bell - Test 1", page_icon="🔔", layout="centered")
st.title("🔔 Universal Call Bell - Test 1")

st.markdown("""
### Before starting
This test checks if the **call bell** works every time it should.

It takes **about one minute**.

The screen will show **6 steps**.  
Each step lasts **10 seconds**.

- When it says **press**, ask the patient to **activate the bell** once.  
- When it says **no press**, ask the patient to **lie down and sit back up naturally**.  
- After each step, tap **T** if the alarm or light comes on, or **F** if nothing happens.

At the end, you can **download the results** as either a **CSV file** or a **PDF file**.
""")

# Setup
if "press_list" not in st.session_state:
	st.session_state.press_list = random.sample(["P"] * 3 + ["N"] * 3, 6)
if "results" not in st.session_state:
	st.session_state.results = [""] * 6
if "finished" not in st.session_state:
	st.session_state.finished = False

# Run test
if not st.session_state.finished and st.button("Start Test"):
	placeholder = st.empty()
	for i, label in enumerate(st.session_state.press_list, 1):
		with placeholder.container():
			st.markdown(f"## Step {i}/6")
			if label == "P":
				st.warning("Ask the patient to **activate the bell now**.")
			else:
				st.warning("Ask the patient to **lie down and sit back up naturally**.")
			st.session_state.results[i - 1] = st.radio(
				"Did it activate? Select either **T** or **F**:",
				["T", "F"],
				horizontal=True,
				key=f"trial_{i}",
			)
			st.caption("Next step in 10 seconds...")
		time.sleep(10)
	placeholder.empty()
	st.session_state.finished = True
	st.success("All steps done. Download the results below.")

# Download section
if st.session_state.finished:
	df = pd.DataFrame(
		{"Press List": st.session_state.press_list, "Activated?": st.session_state.results},
		index=[1, 2, 3, 4, 5, 6],
	)

	# CSV
	csv_buffer = BytesIO()
	df.to_csv(csv_buffer, index=True)
	st.download_button(
		label="📥 Download Results (CSV)",
		data=csv_buffer.getvalue(),
		file_name="call_bell_test_results.csv",
		mime="text/csv",
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
		pdf.cell(60, 10, df.iloc[i, 0], 1, 0, "C")
		pdf.cell(60, 10, df.iloc[i, 1], 1, 1, "C")
	pdf_buffer = BytesIO(pdf.output(dest="S").encode("latin1"))
	st.download_button(
		label="📄 Download Results (PDF)",
		data=pdf_buffer,
		file_name="call_bell_test_results.pdf",
		mime="application/pdf",
	)

	st.dataframe(df)
