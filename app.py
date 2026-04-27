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


def main():
	st.set_page_config(
		page_title="CDSS - Diabetes Risk Assessment", 
		page_icon="🏥",
		layout="wide"
	)

	# Simple Professional Header
	st.markdown("# 🏥 Diabetes Risk Assessment")
	st.markdown("**Clinical Decision Support System** - Rule-based evaluation")

	# Simple Disclaimer
	st.info("⚕️ **Clinical Tool**: Uses evidence-based rules, not AI/ML. For healthcare professional use only.")

	st.sidebar.header("Patient Data")
	st.sidebar.caption("Enter clinical parameters")
	age = st.sidebar.number_input("Patient Age (years)", min_value=1, max_value=120, value=40)
	bmi = st.sidebar.number_input("Body Mass Index (BMI)", min_value=10.0, max_value=60.0, value=24.0, step=0.1)
	glucose = st.sidebar.number_input(
		"Fasting Blood Glucose (mg/dL)", min_value=50.0, max_value=400.0, value=100.0, step=1.0
	)
	hba1c = st.sidebar.number_input(
		"HbA1c (%)", min_value=3.0, max_value=15.0, value=5.6, step=0.1
	)
	hypertension = st.sidebar.selectbox("Hypertension History", options=[0, 1], index=0, format_func=lambda x: "Yes" if x else "No")
	heart_disease = st.sidebar.selectbox("Heart Disease History", options=[0, 1], index=0, format_func=lambda x: "Yes" if x else "No")
	smoking = st.sidebar.selectbox("Smoking Status", options=["Never", "Former", "Current"])

	analyze = st.sidebar.button("Analyze", type="primary", use_container_width=True)

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

		# Clinical Report Header
		st.markdown("---")
		st.markdown("## 📄 CLINICAL EVALUATION REPORT")
		st.markdown(f"**Date:** {pd.Timestamp.now().strftime('%B %d, %Y')} | **System:** Rule-Based Clinical Decision Support")

		# Patient Summary
		st.markdown("### 👤 Patient Summary")
		summary_cols = st.columns(4)
		with summary_cols[0]:
			st.metric("Age", f"{age} years")
		with summary_cols[1]:
			st.metric("BMI", f"{bmi:.1f}")
		with summary_cols[2]:
			st.metric("Glucose", f"{glucose} mg/dL")
		with summary_cols[3]:
			st.metric("HbA1c", f"{hba1c:.1f}%")

		# Risk Assessment Result
		st.markdown("---")
		st.markdown("## 📊 RISK ASSESSMENT RESULT")

		# Risk Level with Clinical Formatting
		if final_risk == "High":
			st.error(f"### ⚠️ RISK LEVEL: {risk_text}")
			st.markdown("*Immediate clinical attention required*")
		elif final_risk == "Medium":
			st.warning(f"### ⚡ RISK LEVEL: {risk_text}")
			st.markdown("*Clinical monitoring recommended*")
		else:
			st.success(f"### ✅ RISK LEVEL: {risk_text}")
			st.markdown("*Routine screening appropriate*")

		# Clinical Rationale
		st.markdown("---")
		st.markdown("## 🔍 CLINICAL RATIONALE")

		# Activated Rules Table
		if active_rules:
			st.markdown("### Activated Clinical Rules")
			rules_data = []
			for rule in active_rules:
				rules_data.append({
					"Rule ID": rule['rule_id'],
					"Clinical Condition": rule['if'],
					"Risk Implication": rule['then']
				})
			st.dataframe(rules_data, use_container_width=True)
		else:
			st.info("ℹ️ No clinical rules were activated. Risk assessment defaults to Low Risk based on current parameters.")

		# Decision Process
		st.markdown("### Decision Process Summary")
		high_count = sum(1 for r in active_rules if r["level"] == "High")
		medium_count = sum(1 for r in active_rules if r["level"] == "Medium")
		low_count = sum(1 for r in active_rules if r["level"] == "Low")

		process_info = f"""
		**Rule Evaluation:** {len(RULES)} clinical IF-THEN rules evaluated against patient parameters

		**Rule Activation:** {len(active_rules)} rule(s) activated
		- High Risk Rules: {high_count}
		- Medium Risk Rules: {medium_count}
		- Low Risk Rules: {low_count}

		**Conflict Resolution:** Priority hierarchy applied (High > Medium > Low)

		**Final Assessment:** {final_risk} Risk Category
		"""
		st.markdown(process_info)

		# Clinical Recommendations
		st.markdown("---")
		st.markdown("## 🏥 Clinical Recommendations")

		if final_risk == "High":
			recommendations = [
				{"Action": "Schedule comprehensive diabetes evaluation within 1 week", "Rationale": "Multiple high-risk factors detected"},
				{"Action": "Order HbA1c, fasting glucose, and OGTT tests", "Rationale": "Confirm diabetes diagnosis"},
				{"Action": "Initiate lifestyle intervention program", "Rationale": "Address modifiable risk factors"},
				{"Action": "Quarterly follow-up for 6 months", "Rationale": "Close monitoring required"},
				{"Action": "Consider endocrinology consultation", "Rationale": "Specialist management may be needed"}
			]
		elif final_risk == "Medium":
			recommendations = [
				{"Action": "Schedule diabetes screening within 3 months", "Rationale": "Moderate risk factors present"},
				{"Action": "Order HbA1c and fasting glucose tests", "Rationale": "Screen for prediabetes/diabetes"},
				{"Action": "Provide lifestyle counseling", "Rationale": "Prevent progression through behavior change"},
				{"Action": "Annual follow-up with risk reassessment", "Rationale": "Regular monitoring needed"},
				{"Action": "Consider metformin if prediabetes confirmed", "Rationale": "Prevent diabetes onset"}
			]
		else:  # Low
			recommendations = [
				{"Action": "Continue routine diabetes screening", "Rationale": "Low risk allows standard intervals"},
				{"Action": "Provide diabetes prevention education", "Rationale": "Maintain risk factor awareness"},
				{"Action": "Encourage healthy lifestyle", "Rationale": "Prevent risk factor development"},
				{"Action": "Reassess risk factors every 3 years", "Rationale": "Long-term monitoring"},
				{"Action": "Focus on cardiovascular health", "Rationale": "Comprehensive preventive care"}
			]

		st.dataframe(recommendations, use_container_width=True)

		# System Information
		st.markdown("---")
		st.markdown("## 📋 SYSTEM INFORMATION")
		st.markdown(f"""
		**Assessment Method:** Rule-Based Clinical Decision Support System  
		**Knowledge Base:** {len(RULES)} evidence-based clinical rules  
		**Evidence Level:** Based on {len(active_rules)} activated clinical rules  
		**System Type:** Deterministic rule engine (No probabilistic modeling)  
		**Traceability:** Full clinical decision logic documented above
		""")

		st.info("⚕️ **Clinical Note:** For healthcare professional use. Final decisions by qualified clinicians only.")

	else:
		st.info("👤 Enter patient data in the sidebar and click 'Assess Risk' to get clinical recommendations.")
