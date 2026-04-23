import streamlit as st
import pandas as pd
from inference import evaluate_rules, resolve_conflict
from rules import RULES


def risk_style(level):
	if level == "High":
		return "#ff4d4f", "#fff1f0", "RISIKO TINGGI"
	if level == "Medium":
		return "#faad14", "#fffbe6", "RISIKO SEDANG"
	return "#52c41a", "#f6ffed", "RISIKO RENDAH"


def normalize_smoking(value):
	"""Normalisasi nilai smoking_history dari dataset ke format rule engine."""
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
	"""Standarisasi nama kolom dataset agar sesuai input rule-based engine."""
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
	st.set_page_config(page_title="CDSS Diabetes Tipe 2", layout="wide")

	st.title("Clinical Decision Support System (Rule-Based)")
	st.subheader("Deteksi Dini Diabetes Melitus Tipe 2")
	st.caption(
		"Pendekatan: Knowledge-based IF-THEN, forward chaining, conflict handling, dan decision traceability."
	)
	st.info("Sistem ini tidak menggunakan machine learning atau training model.")

	tab_single, tab_batch = st.tabs(["Analisis Individu", "Analisis Batch CSV"])

	with tab_single:
		st.sidebar.header("Input Parameter Klinis")
		age = st.sidebar.number_input("Usia (tahun)", min_value=1, max_value=120, value=40)
		bmi = st.sidebar.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0, step=0.1)
		glucose = st.sidebar.number_input(
			"Glukosa darah (mg/dL)", min_value=50.0, max_value=400.0, value=100.0, step=1.0
		)
		hba1c = st.sidebar.number_input(
			"HbA1c (%)", min_value=3.0, max_value=15.0, value=5.6, step=0.1
		)
		hypertension = st.sidebar.selectbox("Hipertensi", options=[0, 1], index=0)
		heart_disease = st.sidebar.selectbox("Penyakit Jantung", options=[0, 1], index=0)
		smoking = st.sidebar.selectbox("Status Merokok", options=["Never", "Former", "Current"])

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
					<h3 style="margin: 0; color: {border_color};">Hasil Analisis: {risk_text}</h3>
				</div>
				""",
				unsafe_allow_html=True,
			)

			st.write("")
			st.subheader("Traceability (Rule Aktif)")

			if active_rules:
				st.table(active_rules)
				active_rule_ids = ", ".join([rule["rule_id"] for rule in active_rules])
				st.caption(f"Rule aktif: {active_rule_ids}")
			else:
				st.info("Tidak ada rule yang aktif. Sistem menetapkan risiko rendah secara default.")

			st.subheader("Alur Keputusan")
			high_count = sum(1 for r in active_rules if r["level"] == "High")
			medium_count = sum(1 for r in active_rules if r["level"] == "Medium")
			low_count = sum(1 for r in active_rules if r["level"] == "Low")

			st.markdown(
				"\n".join(
					[
						f"1. Sistem membaca basis pengetahuan klinis berupa {len(RULES)} rule IF-THEN (R1-R30).",
						"2. Forward chaining mengevaluasi semua rule terhadap data pasien.",
						f"3. Rule aktif ditemukan: {len(active_rules)} (High={high_count}, Medium={medium_count}, Low={low_count}).",
						"4. Conflict handling diterapkan dengan prioritas High > Medium > Low.",
						f"5. Keputusan akhir: {final_risk}.",
					]
				)
			)
		else:
			st.info("Isi parameter di sidebar lalu klik tombol Analyze untuk memulai evaluasi.")

	with tab_batch:
		st.subheader("Evaluasi Batch Dataset Simulasi")
		st.caption("Unggah CSV (misalnya dari Kaggle) untuk menguji konsistensi inferensi rule-based pada data skala besar.")

		uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])
		if uploaded_file is not None:
			raw_df = pd.read_csv(uploaded_file, sep=None, engine="python")
			st.write(f"Jumlah data mentah: {len(raw_df):,} baris")

			try:
				prepared_df, dropped_count = prepare_batch_dataframe(raw_df)
			except ValueError as exc:
				st.error(str(exc))
				st.stop()

			st.write(f"Data valid setelah cleaning: {len(prepared_df):,} baris")
			if dropped_count > 0:
				st.warning(f"Baris yang dihapus karena nilai tidak valid/kosong: {dropped_count:,}")

			if st.button("Analyze Batch", type="primary"):
				result_df, summary = evaluate_batch(prepared_df)
				total = summary["total_records"]

				st.subheader("Ringkasan Hasil Evaluasi")
				col1, col2, col3, col4 = st.columns(4)
				col1.metric("Total Data", f"{total:,}")
				col2.metric("Kasus Tanpa Rule Aktif", f"{summary['no_active_count']:,}")
				col3.metric("Kasus Multi-Rule", f"{summary['multi_rule_count']:,}")
				col4.metric("Jumlah Rule Basis Pengetahuan", f"{len(RULES)}")

				risk_df = pd.DataFrame(
					[
						{"Risk": "High", "Count": summary["risk_counts"]["High"]},
						{"Risk": "Medium", "Count": summary["risk_counts"]["Medium"]},
						{"Risk": "Low", "Count": summary["risk_counts"]["Low"]},
					]
				)
				risk_df["Percentage"] = (risk_df["Count"] / total * 100).round(2)

				st.subheader("Distribusi Tingkat Risiko")
				st.dataframe(risk_df, use_container_width=True)

				rule_freq_df = pd.DataFrame(
					[
						{"Rule": rule_id, "Activation_Count": count}
						for rule_id, count in summary["rule_counts"].items()
					]
				).sort_values(by="Activation_Count", ascending=False)
				st.subheader("Frekuensi Aktivasi Rule (R1-R30)")
				st.dataframe(rule_freq_df, use_container_width=True)

				st.subheader("Contoh Hasil Traceability (100 baris pertama)")
				st.dataframe(result_df.head(100), use_container_width=True)

				csv_output = result_df.to_csv(index=False).encode("utf-8")
				st.download_button(
					"Download Hasil Evaluasi (CSV)",
					data=csv_output,
					file_name="hasil_evaluasi_cdss_rule_based.csv",
					mime="text/csv",
				)

				with st.expander("Catatan Metodologi Batch"):
					st.write("Dataset digunakan sebagai data simulasi untuk menguji logika inferensi rule-based.")
					st.write("Tidak ada proses training model, fitting parameter, atau algoritma machine learning.")
		else:
			st.info("Silakan unggah file CSV untuk memulai evaluasi batch.")


if __name__ == "__main__":
	main()
