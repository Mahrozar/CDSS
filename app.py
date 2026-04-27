import streamlit as st
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

	st.title("🏥 Clinical Decision Support System")
	st.subheader("Type 2 Diabetes Risk Assessment & Management")
	st.caption("Evidence-based rule engine for clinical decision making | Full traceability | No machine learning")

	st.sidebar.header("🏥 Patient Assessment")
	st.sidebar.caption("Enter clinical parameters for risk evaluation")
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

	analyze = st.sidebar.button("🔍 Assess Risk", type="primary")

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

		# Risk Level Result
		st.markdown("---")
		st.subheader("📊 RESULT")
		st.markdown(f"### Risk Level: **{risk_text}**")
		st.markdown("---")

		# Explanation Section
		st.subheader("🔍 EXPLANATION")

		# Activated Rules Table
		if active_rules:
			rules_data = []
			for rule in active_rules:
				rules_data.append({
					"Rule ID": rule['rule_id'],
					"Condition": rule['if'],
					"Conclusion": rule['then']
				})
			st.markdown("**Activated Rules:**")
			st.dataframe(rules_data, use_container_width=True)
		else:
			st.info("No clinical rules were activated. System defaults to Low Risk.")

		# Decision Process Summary
		high_count = sum(1 for r in active_rules if r["level"] == "High")
		medium_count = sum(1 for r in active_rules if r["level"] == "Medium")
		low_count = sum(1 for r in active_rules if r["level"] == "Low")

		st.markdown("**Decision Process:**")
		process_summary = f"""
		- **Input Collection**: Clinical parameters collected from sidebar input
		- **Rule Evaluation**: System evaluated {len(RULES)} IF-THEN rules against patient data
		- **Rule Activation**: {len(active_rules)} rule(s) activated (High: {high_count}, Medium: {medium_count}, Low: {low_count})
		- **Conflict Resolution**: Priority applied: High > Medium > Low
		- **Final Decision**: Risk assessment: {final_risk}
		"""
		st.markdown(process_summary)

		st.markdown("---")

		# Clinical Recommendations Section
		st.subheader("🏥 CLINICAL RECOMMENDATION")
		if final_risk == "High":
			recommendations = [
				{"Priority": "Immediate", "Action": "Schedule comprehensive diabetes evaluation within 1 week", "Rationale": "Multiple high-risk factors detected requiring urgent assessment"},
				{"Priority": "Diagnostic", "Action": "Order HbA1c, fasting glucose, and oral glucose tolerance test", "Rationale": "Confirm diabetes diagnosis with gold-standard tests"},
				{"Priority": "Lifestyle", "Action": "Initiate intensive lifestyle intervention program", "Rationale": "Address modifiable risk factors through diet and exercise"},
				{"Priority": "Monitoring", "Action": "Quarterly follow-up for 6 months, then every 6 months", "Rationale": "Close monitoring required for high-risk patients"},
				{"Priority": "Referral", "Action": "Consider endocrinology consultation if diagnosis confirmed", "Rationale": "Specialist management may be needed for complex cases"}
			]
		elif final_risk == "Medium":
			recommendations = [
				{"Priority": "Assessment", "Action": "Schedule diabetes screening within 3 months", "Rationale": "Moderate risk factors warrant timely evaluation"},
				{"Priority": "Diagnostic", "Action": "Order HbA1c and fasting glucose tests", "Rationale": "Screen for prediabetes or diabetes"},
				{"Priority": "Lifestyle", "Action": "Provide lifestyle counseling and education", "Rationale": "Prevent progression through behavior modification"},
				{"Priority": "Monitoring", "Action": "Annual follow-up with risk factor reassessment", "Rationale": "Regular monitoring for risk factor changes"},
				{"Priority": "Prevention", "Action": "Consider metformin if prediabetes confirmed", "Rationale": "Pharmacologic intervention may prevent diabetes onset"}
			]
		else:  # Low
			recommendations = [
				{"Priority": "Screening", "Action": "Continue routine diabetes screening per guidelines", "Rationale": "Low risk allows standard screening intervals"},
				{"Priority": "Education", "Action": "Provide general diabetes prevention education", "Rationale": "Maintain awareness of risk factors"},
				{"Priority": "Lifestyle", "Action": "Encourage healthy lifestyle maintenance", "Rationale": "Prevent risk factor development"},
				{"Priority": "Monitoring", "Action": "Reassess risk factors every 3 years", "Rationale": "Long-term monitoring for risk factor changes"},
				{"Priority": "Wellness", "Action": "Focus on overall cardiovascular health", "Rationale": "Comprehensive preventive care approach"}
			]

		st.dataframe(recommendations, use_container_width=True)
		st.caption(f"**Risk Category: {final_risk}** | **System Type:** Rule-based Clinical Decision Support | **Evidence Level:** Based on {len(active_rules)} activated clinical rules")

		st.caption("**System Note:** This is a rule-based clinical decision support system with full traceability. No machine learning algorithms used.")
	else:
		st.info("👤 Enter patient information in the sidebar and click 'Assess Risk' to generate clinical recommendations.")


if __name__ == "__main__":
	main()
