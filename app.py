import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="Drug Interaction Platform")

st.title("💊 Drug Interaction Intelligence Platform")
st.caption("Mechanistic, Pharmacokinetic and Clinical Interaction Analysis")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("full_pharma_dataset_50drugs_all_pairs.csv")

data = load_data()

drug_list = sorted(set(data['Drug1']).union(set(data['Drug2'])))

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    drug1 = st.selectbox("Select Drug 1", drug_list)

with col2:
    drug2 = st.selectbox("Select Drug 2", drug_list)

# ---------------- PUBCHEM ----------------
def get_pubchem_data(drug):
    try:
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug}/cids/JSON"
        cid = requests.get(cid_url).json()['IdentifierList']['CID'][0]

        img = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        link = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"

        return img, link
    except:
        return None, None

# ---------------- RISK SCORE ----------------
def calculate_risk(severity):
    return {
        "Minor": 3,
        "Moderate": 6,
        "Major": 9
    }.get(severity, 5)

# ---------------- BUTTON ----------------
if st.button("Analyze Interaction"):

    # ---------- FIND DATA ----------
    row = data[
        ((data['Drug1'] == drug1) & (data['Drug2'] == drug2)) |
        ((data['Drug1'] == drug2) & (data['Drug2'] == drug1))
    ]

    st.divider()

    if len(row) > 0:

        r = row.iloc[0]

        severity = r["Severity"]
        risk_score = calculate_risk(severity)

        # =============================
        # SUMMARY
        # =============================
        st.subheader("Interaction Summary")

        colA, colB, colC = st.columns(3)

        with colA:
            st.metric("Confidence", "100% (Dataset-based)")

        with colB:
            if severity == "Major":
                st.error("MAJOR")
            elif severity == "Moderate":
                st.warning("MODERATE")
            else:
                st.success("MINOR")

        with colC:
            st.metric("Risk Score (0–10)", risk_score)

        # =============================
        # GAUGE
        # =============================
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Score"},
            gauge={
                'axis': {'range': [0, 10]},
                'steps': [
                    {'range': [0, 4], 'color': "green"},
                    {'range': [4, 7], 'color': "orange"},
                    {'range': [7, 10], 'color': "red"},
                ],
            }
        ))

        st.plotly_chart(fig_gauge, use_container_width=True)

        # =============================
        # GRAPH
        # =============================
        st.subheader("Interaction Analysis Graph")

        colG1, colG2 = st.columns(2)

        # Bar graph
        with colG1:
            fig_bar = go.Figure(go.Bar(
                x=["Minor", "Moderate", "Major"],
                y=[
                    2 if severity == "Minor" else 0.5,
                    5 if severity == "Moderate" else 0.5,
                    8 if severity == "Major" else 0.5,
                ]
            ))
            st.plotly_chart(fig_bar, use_container_width=True)

        # Pie graph
        with colG2:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Confidence", "Uncertainty"],
                values=[100, 0],
                hole=0.5
            )])
            st.plotly_chart(fig_pie, use_container_width=True)

        # =============================
        # STRUCTURES
        # =============================
        st.subheader("Chemical Structures")

        c1, c2 = st.columns(2)

        with c1:
            img, link = get_pubchem_data(drug1)
            st.write(f"### {drug1}")
            if img:
                st.image(img, width=250)
                st.markdown(f"[View on PubChem]({link})")

        with c2:
            img, link = get_pubchem_data(drug2)
            st.write(f"### {drug2}")
            if img:
                st.image(img, width=250)
                st.markdown(f"[View on PubChem]({link})")

        # =============================
        # DETAILS
        # =============================
        tab1, tab2, tab3, tab4 = st.tabs([
            "Overview",
            "Mechanism",
            "PK/PD",
            "Clinical"
        ])

        with tab1:
            st.info(r["Interaction"])
            st.write("### Evidence")
            st.success(r["Evidence_Type"])

        with tab2:
            st.write("### Mechanism")
            st.write(r["Mechanism"])
            st.write("### Cytochrome")
            st.warning(r["Cytochrome"])

        with tab3:
            st.write("### Pharmacokinetics")
            st.write(r["Pharmacokinetics"])
            st.write("### Pharmacodynamics")
            st.write(r["Pharmacodynamics"])

        with tab4:
            st.write("### Dose Consideration")
            st.write(r["Dose_Consideration"])

            st.write("### Therapeutic Index")
            st.write(r["Therapeutic_Index"])

            st.write("### Onset")
            st.write(r["Onset"])

            st.write("### Route Impact")
            st.write(r["Route_Impact"])

            st.write("### Patient Factors")
            st.write(r["Patient_Factors"])

            st.write("### Clinical Advice")
            st.error(r["Clinical_Advice"])

            st.write("### Explanation")
            for point in str(r["Why_Explanation"]).split(";"):
                st.write("•", point.strip())

    else:
        st.warning("No interaction found in dataset")

    st.divider()
    st.caption("For research and educational use only")