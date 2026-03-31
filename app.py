import streamlit as st
import pandas as pd

st.set_page_config(page_title="ASTRA Resource Screener", layout="wide", page_icon="📊")

st.title("📊 ASTRA - Demand vs Supply Matching Engine")
st.markdown("**NSE-style Resource Utilization Screener** for Workforce Planning & Resource Allocation")

# ====================== DATA ======================
@st.cache_data
def load_data():
    projects_data = {
        'Project Name': ['Astrazeneca', 'Stryker', 'Prudential Insurance', 'Walmartlabs', 'Newell Brands', 'Humana Insurance', 'Pfizer', 'Google'],
        'Required Skill 1': ['Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci'],
        'Required Skill 2': ['6 Sigma', 'PgMP', 'SAFe', 'PMP', 'SAFe', 'Canva', 'SAFe', 'PMP'],
        'Required Skill 3': ['PMP', 'Canva', '6 Sigma', 'SAFe', 'Articulate', 'EnableNow', 'Articulate', '6 Sigma'],
        'Geography': ['Noida', 'Noida', 'Pune', 'Bengaluru', 'Noida', 'Bengaluru', 'Pune', 'Pune']
    }
    projects_df = pd.DataFrame(projects_data)

    resources_data = {
        'Employee Name': ['Jaya', 'Shoumo', 'Shreyansh', 'Animesh', 'Amit', 'Shaveta', 'Varnika', 'Vandita', 'TK', 'Sonia', 'Shivansh', 'Divya', 'Rekha', 'Ranjeet', 'Tony Stark', 'Bruce Banner', 'Steven Strange', 'Natasha', 'Nick Fury'],
        'Current Status': ['Billable', 'Billable', 'Billable', 'On Bench', 'On Bench', 'On Bench', 'Billable', 'Billable', 'Billable', 'On Bench', 'Billable', 'On Bench', 'On Bench', 'Billable', 'On Bench', 'On Bench', 'Billable', 'Billable', 'Billable'],
        'Skill 1': ['Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'EnableNow', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Prosci', 'Articulate', 'Prosci', 'Prosci'],
        'Skill 2': ['6 Sigma', 'PgMP', '', 'PMP', '', 'SAFe', 'SAFe', 'PMP', 'PMP', 'PMP', 'PMP', 'PMP', 'PMP', 'EnableNow', 'PMP', 'EnableNow', 'PMP', 'PMP', 'PMP'],
        'Skill 3': ['PgMP', '', '6 Sigma', 'SAFe', '', '', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma', '6 Sigma'],
        'Geography': ['Noida', 'Noida', 'Pune', 'Bengaluru', 'Noida', 'Bengaluru', 'Pune', 'Pune', 'Noida', 'Bengaluru', 'Bengaluru', 'Bengaluru', 'Pune', 'Noida', 'Hyderabad', 'Bengaluru', 'Bengaluru', 'Noida', 'Chennai'],
        'Available in (Days)': ['65', '10', '74', 'Immediate', 'Immediate', 'Immediate', '70', '20', '34', 'Immediate', '7', 'Immediate', 'Immediate', '34', 'Immediate', 'Immediate', 'Immediate', '69', '25'],
    }
    resources_df = pd.DataFrame(resources_data)
    return projects_df, resources_df

projects_df, resources_df = load_data()

# ====================== SCORING (Simplified) ======================
def calculate_suitability(project_row, resources_df):
    req_skills = [project_row['Required Skill 1'], project_row.get('Required Skill 2', ''), project_row.get('Required Skill 3', '')]
    req_skills = [s for s in req_skills if str(s).strip() != '']
    proj_geo = project_row['Geography']

    def score_row(row):
        res_skills = [row['Skill 1'], row.get('Skill 2', ''), row.get('Skill 3', '')]
        res_skills = [s for s in res_skills if str(s).strip() != '']
        skill_match = len(set(req_skills) & set(res_skills))
        geo_match = 1 if row['Geography'] == proj_geo else 0
        
        avail = str(row['Available in (Days)']).strip().lower()
        if avail == 'immediate':
            avail_score = 1
        else:
            days = int(avail)
            avail_score = 4 if days <= 14 else 3 if days <= 30 else 2 if days <= 60 else 1
        
        suitability = avail_score + skill_match + geo_match
        return pd.Series({
            'Suitability Score': suitability,
            'Skill Match': skill_match,
            'Geo Matched': 'Yes' if geo_match else '-',
            'Available in (Days)': row['Available in (Days)']
        })

    scored = resources_df.apply(score_row, axis=1)
    result = pd.concat([resources_df[['Employee Name', 'Current Status']], scored], axis=1)
    result = result.sort_values('Suitability Score', ascending=False).reset_index(drop=True)
    result.insert(0, 'Rank', result.index + 1)
    return result

# ====================== MAIN APP (Minimal) ======================
st.subheader("📌 Testing with Humana Insurance (Bengaluru)")
project_row = projects_df[projects_df['Project Name'] == 'Humana Insurance'].iloc[0]

result_df = calculate_suitability(project_row, resources_df)

col1, col2, col3 = st.columns(3)
col1.metric("Demand", "1 Resource")
col2.metric("High-Fit Resources (≥4)", len(result_df[result_df['Suitability Score'] >= 4]))
col3.metric("Total Resources", len(result_df))

st.dataframe(
    result_df.style.background_gradient(subset=['Suitability Score'], cmap='RdYlGn'),
    use_container_width=True,
    hide_index=True
)

st.success("✅ Minimal version loaded successfully! If this works, we’ll add Custom Scenario + filters next.")
