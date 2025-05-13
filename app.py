#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 03:13:33 2025

@author: merajalam
"""
import streamlit as st
import pandas as pd
import gdown

# Google Drive file (shared with 'anyone can view')
GOOGLE_DRIVE_FILE_URL = "https://drive.google.com/uc?id=1W5bEfzU9Z42if5PeNjQG6DFie9ryOOvS"

@st.cache_data
def load_data():
    output_file = "jee_cutoff_data.xlsx"
    gdown.download(GOOGLE_DRIVE_FILE_URL, output_file, quiet=False)
    df = pd.read_excel(output_file)
    return df

def filter_colleges(df, student_category, category_rank, crl_rank, gender, branch, quota):
    student_category = student_category.upper()
    gender = gender.lower()

    eligible_rows = []

    for _, row in df.iterrows():
        seat_category = str(row['Category']).upper()
        seat_gender = str(row['Gender']).lower()
        seat_quota = str(row['Quota']).lower()
        seat_branch = row['Branch']
        closing_rank = row['ClosingRank']

        if seat_gender == "female-only (including supernumerary)" and gender != "female":
            continue  # Male not eligible for female-only seats

        if quota.lower() != "all" and seat_quota != quota.lower():
            continue

        if branch and seat_branch not in branch:
            continue
        margin_factor = 1.20
        # Apply logic based on eligibility
        if seat_category == "OPEN":
            if crl_rank <= closing_rank *margin_factor:
                eligible_rows.append(row)
        elif seat_category == student_category:
            if category_rank <= closing_rank *(margin_factor-0.05):
                eligible_rows.append(row)

    return pd.DataFrame(eligible_rows).sort_values(by="ClosingRank")

def main():
    st.set_page_config(page_title="JEE Main College Predictor", layout="wide")
    st.title("JEE Main College Predictor")
    st.markdown("Get a personalized list of eligible NITs, IIITs, and GFTIs based on your JEE Main rank.")

    df = load_data()

    categories = sorted(df['Category'].dropna().unique())
    branches = sorted(df['Branch'].dropna().unique())

    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("Select Your Category", options=categories, key="cat_select")
    with col2:
        category_rank = st.number_input(f"Enter Your {category} Rank", min_value=1, step=1, key="cat_rank")
    with col3:
        crl_rank = st.number_input("Enter Your CRL (Common Rank List) Rank", min_value=1, step=1, key="crl_rank")

    col4, col5 = st.columns(2)
    with col4:
        gender = st.selectbox("Select Your Gender", options=["Male", "Female"], key="gender_select")
    with col5:
        quota = st.selectbox("Select Your Quota", options=["All", "HS", "OS"], key="quota_select")


    # Always show multiselect
    selected_branches = st.multiselect(
        "Select Preferred Branches(OPTIONAl):",
        options=branches,
        key="branch_multiselect"
    ) 

    if st.button("🔍 Find Eligible Colleges", key="predict_button"):
        branch_filter = selected_branches if selected_branches else None

        results = filter_colleges(
            df,
            student_category=category,
            category_rank=category_rank,
            crl_rank=crl_rank,
            gender=gender,
            branch=branch_filter,
            quota=quota
        )

        if not results.empty:
            st.success(f"Found {len(results)} eligible college seats.")
            st.dataframe(results.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("No eligible colleges found for the given Rank.")

if __name__ == "__main__":
    main()