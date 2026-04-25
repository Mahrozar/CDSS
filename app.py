import streamlit as st
import pandas as pd
from inference import evaluate_rules, resolve_conflict
from rules import RULES


def risk_style(level):
	if level == "High":
		return "#ff4d4f", "#fff1f0", "HIGH RISK"
	if level == "Medium":
		return "#faad14", "#fffbe6", "MEDIUM RISK"
	return "#52c41a", "#f6ffed", "LOW RISK"


def normalize_smoking(value):
	"""Normalize smoking_history values from dataset to rule engine format."""
	if value is None:
		return "Unknown"

	v = str(value).strip().lower()
	mapping = {
		"never": "Never",
		"not current": "Former",
		"former": "Former",
		"ever": "Former",
		"current": "Current",
		"no info": "Unknown",
		"unknown": "Unknown",
		"nan": "Unknown",
		"none": "Unknown",
	}
	return mapping.get(v, "Unknown")


def prepare_batch_dataframe(df):
	"""Standardize dataset column names to match rule-based engine inputs."""
	normalized = df.copy()
	normalized.columns = [str(col).strip().lower() for col in normalized.columns]

	renamed = normalized.rename(
		columns={
			"blood_glucose_level": "glucose",
			"hba1c_level": "hba1c",
			"smoking_history": "smoking",
		}
	)

	required = ["age", "bmi", "glucose", "hba1c", "hypertension", "heart_disease", "smoking"]
	missing = [col for col in required if col not in renamed.columns]
	if missing:
		available = ", ".join(renamed.columns.astype(str).tolist())
		raise ValueError(
			f"Kolom wajib tidak ditemukan: {', '.join(missing)}. Kolom yang terbaca: {available}"
		)

	prepared = renamed[required].copy()
	prepared["age"] = pd.to_numeric(prepared["age"], errors="coerce")
	prepared["bmi"] = pd.to_numeric(prepared["bmi"], errors="coerce")
	prepared["glucose"] = pd.to_numeric(prepared["glucose"], errors="coerce")
	prepared["hba1c"] = pd.to_numeric(prepared["hba1c"], errors="coerce")
	prepared["hypertension"] = pd.to_numeric(prepared["hypertension"], errors="coerce")
	prepared["heart_disease"] = pd.to_numeric(prepared["heart_disease"], errors="coerce")	
	prepared["smoking"] = prepared["smoking"].apply(normalize_smoking)

	before = len(prepared)
	prepared = prepared.dropna()
	after = len(prepared)
	dropped = before - after

	prepared["age"] = prepared["age"].astype(int)
	prepared["hypertension"] = prepared["hypertension"].astype(int)
	prepared["heart_disease"] = prepared["heart_disease"].astype(int)

	return prepared, dropped


def evaluate_batch(prepared):
	"""Evaluasi dataset simulasi secara batch dengan forward chaining."""
	rule_counts = {rule["id"]: 0 for rule in RULES}
	risk_counts = {"High": 0, "Medium": 0, "Low": 0}
	no_active_count = 0
	multi_rule_count = 0
	results = []

	for record in prepared.to_dict(orient="records"):
		active_rules = evaluate_rules(record)
		risk_level = resolve_conflict(active_rules)
		active_ids = [rule["rule_id"] for rule in active_rules]

		risk_counts[risk_level] += 1
		if not active_ids:
			no_active_count += 1
		if len(active_ids) > 1:
			multi_rule_count += 1
		for rule_id in active_ids:
			rule_counts[rule_id] += 1

		results.append(
			{
				"risk_level": risk_level,
				"active_rule_count": len(active_ids),
				"active_rules": ", ".join(active_ids),
			}
		)

	result_df = prepared.copy()
	result_df["risk_level"] = [r["risk_level"] for r in results]
	result_df["active_rule_count"] = [r["active_rule_count"] for r in results]
	result_df["active_rules"] = [r["active_rules"] for r in results]

	summary = {
		"total_records": len(prepared),
		"risk_counts": risk_counts,
		"no_active_count": no_active_count,
		"multi_rule_count": multi_rule_count,
		"rule_counts": rule_counts,
	}
	return result_df, summary


def main():
	st.set_page_config(page_title="CDSS Diabetes Type 2", layout="wide")

	st.title("Clinical Decision Support System (Rule-Based)")
	st.subheader("Early Detection of Type 2 Diabetes Mellitus")
	st.caption(
		"Approach: Knowledge-based IF-THEN, forward chaining, conflict handling, and decision traceability."
	)
	st.info("This system does not use machine learning or training models.")
	st.markdown(
		"""
		**Demo Statement:**  
		"This system demonstrates how clinical guidelines are operationalized into a rule-based decision support system, ensuring transparency, explainability, and clinical interpretability."
		"""
	)

	tab_single, tab_batch = st.tabs(["Individual Analysis", "Batch CSV Analysis"])

	with tab_single:
		st.sidebar.header("Clinical Input Parameters")
		age = st.sidebar.number_input("Age (years)", min_value=1, max_value=120, value=40)
		bmi = st.sidebar.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0, step=0.1)
		glucose = st.sidebar.number_input(
			"Blood glucose (mg/dL)", min_value=50.0, max_value=400.0, value=100.0, step=1.0
		)
		hba1c = st.sidebar.number_input(
			"HbA1c (%)", min_value=3.0, max_value=15.0, value=5.6, step=0.1
		)
		hypertension = st.sidebar.selectbox("Hypertension", options=[0, 1], index=0)
		heart_disease = st.sidebar.selectbox("Heart Disease", options=[0, 1], index=0)
		smoking = st.sidebar.selectbox("Smoking Status", options=["Never", "Former", "Current"])

		analyze = st.sidebar.button("Analyze", type="primary")

		if analyze:
			patient_data = {
				"age": int(age),
				"bmi": float(bmi),
				"glucose": float(glucose),
				"hba1c": float(hba1c),
				"hypertension": int(hypertension),
				"heart_disease": int(heart_disease),
				"smoking": smoking,
			}

			active_rules = evaluate_rules(patient_data)
			final_risk = resolve_conflict(active_rules)
			border_color, bg_color, risk_text = risk_style(final_risk)

			st.markdown(
				f"""
				<div style="padding: 16px; border-radius: 10px; border: 2px solid {border_color}; background-color: {bg_color};">
					<h3 style="margin: 0; color: {border_color};">Analysis Result: {risk_text}</h3>
				</div>
				""",
				unsafe_allow_html=True,
			)

			st.write("")
			st.subheader("Why Explanation")
			if active_rules:
				st.write("This risk is determined based on the following clinical rules that are satisfied:")
				for rule in active_rules:
					st.markdown(f"- **{rule['rule_id']}**: {rule['if']} → {rule['then']}")
			else:
				st.info("No rules are satisfied. Low risk is assigned by default.")

			st.subheader("Traceability (Active Rules)")
			if active_rules:
				st.table(active_rules)
				active_rule_ids = ", ".join([rule["rule_id"] for rule in active_rules])
				st.caption(f"Active rules: {active_rule_ids}")
			else:
				st.info("No rules are active. The system assigns low risk by default.")

			st.subheader("Decision Flow (Inference Process)")
			high_count = sum(1 for r in active_rules if r["level"] == "High")
			medium_count = sum(1 for r in active_rules if r["level"] == "Medium")
			low_count = sum(1 for r in active_rules if r["level"] == "Low")

			st.markdown(
				"""
				**Rule-Based Inference Process:**  
				User input → Rule evaluation → Inference engine → Result → Explanation
				"""
			)
			st.markdown(
				"\n".join(
					[
						f"1. **User Input**: Patient data entered (age={age}, BMI={bmi}, glucose={glucose}, HbA1c={hba1c}, hypertension={hypertension}, heart disease={heart_disease}, smoking={smoking}).",
						f"2. **Rule Evaluation**: System evaluates {len(RULES)} IF-THEN rules (R1-R30) against patient data using forward chaining.",
						f"3. **Inference Engine**: Active rules found: {len(active_rules)} (High={high_count}, Medium={medium_count}, Low={low_count}).",
						"4. **Conflict Handling**: High > Medium > Low priority applied if conflicts exist.",
						f"5. **Result**: Final decision: {final_risk}.",
						"6. **Explanation**: WHY explanation displayed based on satisfied rules.",
					]
				)
			)
		else:
			st.info("Fill in the parameters in the sidebar and click Analyze to start evaluation.")

	with tab_batch:
		st.subheader("Batch Dataset Simulation Evaluation")
		st.caption("Upload CSV (e.g., from Kaggle) to test rule-based inference consistency on large-scale data.")

		uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
		if uploaded_file is not None:
			raw_df = pd.read_csv(uploaded_file, sep=None, engine="python")
			st.write(f"Raw data count: {len(raw_df):,} rows")

			try:
				prepared_df, dropped_count = prepare_batch_dataframe(raw_df)
			except ValueError as exc:
				st.error(str(exc))
				st.stop()

			st.write(f"Valid data after cleaning: {len(prepared_df):,} rows")
			if dropped_count > 0:
				st.warning(f"Rows removed due to invalid/empty values: {dropped_count:,}")

			if st.button("Analyze Batch", type="primary"):
				result_df, summary = evaluate_batch(prepared_df)
				total = summary["total_records"]

				st.subheader("Evaluation Summary")
				col1, col2, col3, col4 = st.columns(4)
				col1.metric("Total Data", f"{total:,}")
				col2.metric("Cases Without Active Rules", f"{summary['no_active_count']:,}")
				col3.metric("Multi-Rule Cases", f"{summary['multi_rule_count']:,}")
				col4.metric("Knowledge Base Rules Count", f"{len(RULES)}")

				risk_df = pd.DataFrame(
					[
						{"Risk": "High", "Count": summary["risk_counts"]["High"]},
						{"Risk": "Medium", "Count": summary["risk_counts"]["Medium"]},
						{"Risk": "Low", "Count": summary["risk_counts"]["Low"]},
					]
				)
				risk_df["Percentage"] = (risk_df["Count"] / total * 100).round(2)

				st.subheader("Risk Level Distribution")
				st.dataframe(risk_df, use_container_width=True)

				rule_freq_df = pd.DataFrame(
					[
						{"Rule": rule_id, "Activation_Count": count}
						for rule_id, count in summary["rule_counts"].items()
					]
				).sort_values(by="Activation_Count", ascending=False)
				st.subheader("Rule Activation Frequency (R1-R30)")
				st.dataframe(rule_freq_df, use_container_width=True)

				st.subheader("Traceability Results Sample (First 100 rows)")
				st.dataframe(result_df.head(100), use_container_width=True)

				csv_output = result_df.to_csv(index=False).encode("utf-8")
				st.download_button(
					"Download Evaluation Results (CSV)",
					data=csv_output,
					file_name="cdss_rule_based_evaluation_results.csv",
					mime="text/csv",
				)

				with st.expander("Batch Methodology Notes"):
					st.write("Dataset is used as simulation data to test rule-based inference logic.")
					st.write("No model training, parameter fitting, or machine learning algorithms are involved.")
		else:
			st.info("Please upload a CSV file to start batch evaluation.")


if __name__ == "__main__":
	main()
