import streamlit as st
import pandas as pd

st.set_page_config(page_title="ASTRA Resource Screener", layout="wide", page_icon="📊")

st.title("📊 ASTRA - Demand vs Supply Matching Engine")
st.markdown("**NSE-style Resource Utilization Screener** for Workforce Planning & Resource Allocation")

# ====================== DATA (Clean version - fixed for Streamlit Cloud) ======================
@st.cache_data
def load_data():
    projects_data = {
        'Project ID': [1, 2, 3, 4, 5, 6, 7, 8],
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
        'Next Available Date': [45903, 45848, 45912, 45837, 45837, 45837, 45908, 45858, 45872, 45837, 45845, 45837, 45837, 45872, 45837, 45837, 45838, 45907, 45863]
    }
    resources_df = pd.DataFrame(resources_data)
    return projects_df, resources_df

projects_df, resources_df = load_data()

# ====================== SCORING LOGIC (Exact replica of your Excel Dashboard) ======================
def calculate_suitability(project_row, resources_df):
    req_skills = [project_row['Required Skill 1'], 
                  project_row.get('Required Skill 2', ''), 
                  project_row.get('Required Skill 3', '')]
    req_skills = [s for s in req_skills if pd.notna(s) and str(s).strip() != '']
    proj_geo = project_row['Geography']
    
    def score_row(row):
        res_skills = [row['Skill 1'], row.get('Skill 2', ''), row.get('Skill 3', '')]
        res_skills = [s for s in res_skills if pd.notna(s) and str(s).strip() != '']
        skill_match = len(set(req_skills) & set(res_skills))
        
        geo_match = 1 if row['Geography'] == proj_geo else 0
        
        avail = str(row['Available in (Days)']).strip()
        if avail.lower() == 'immediate':
            avail_days = 0
            avail_score = 1
        else:
            avail_days = int(avail)
            if avail_days <= 14:
                avail_score = 4
            elif avail_days <= 30:
                avail_score = 3
            elif avail_days <= 60:
                avail_score = 2
            else:
                avail_score = 1
        
        suitability = avail_score + skill_match + geo_match
        return pd.Series({
            'Suitability Score': suitability,
            'Skill Match': skill_match,
            'Geo Matched': 'Yes' if geo_match else '-',
            'Availability Score': avail_score,
            'Available in (Days)': row['Available in (Days)'],
            'Next Available Date': row['Next Available Date']
        })
    
    scored = resources_df.apply(score_row, axis=1)
    result = pd.concat([resources_df[['Employee Name', 'Current Status']], scored], axis=1)
    result = result.sort_values('Suitability Score', ascending=False).reset_index(drop=True)
    result.insert(0, 'Rank', result.index + 1)
    return result

# ====================== SIDEBAR ======================
st.sidebar.header("🔍 Select Scenario")

option = st.sidebar.radio("Choose input type", ["Existing Project", "Custom Scenario"])

if option == "Existing Project":
    project_name = st.sidebar.selectbox("Select Project", projects_df['Project Name'])
    project_row = projects_df[projects_df['Project Name'] == project_name].iloc[0]
else:
    st.sidebar.subheader("Custom Scenario")
    project_name = st.sidebar.text_input("Project Name", "Custom Project")
    geo = st.sidebar.selectbox("Geography", ['Bengaluru', 'Noida', 'Pune', 'Hyderabad', 'Chennai'])
    skill1 = st.sidebar.text_input("Required Skill 1", "Prosci")
    skill2 = st.sidebar.text_input("Required Skill 2", "Canva")
    skill3 = st.sidebar.text_input("Required Skill 3", "EnableNow")
    project_row = pd.Series({
        'Project Name': project_name,
        'Geography': geo,
        'Required Skill 1': skill1,
        'Required Skill 2': skill2,
        'Required Skill 3': skill3
    })

# ====================== MAIN DASHBOARD ======================
st.subheader(f"📌 Project: {project_row['Project Name']} | Location: {project_row['Geography']}")
st.caption(f"**Required Skills:** {project_row['Required Skill 1']}, {project_row.get('Required Skill 2', '')}, {project_row.get('Required Skill 3', '')}")

result_df = calculate_suitability(project_row, resources_df)

# Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Demand", "1 Resource")
high_fit = len(result_df[result_df['Suitability Score'] >= 4])
col2.metric("High-Fit Resources (≥4)", high_fit)
col3.metric("Immediate / Near-term", len(result_df[result_df['Available in (Days)'].apply(lambda x: str(x).strip().lower() in ['immediate', '7', '10', '20'])]))
col4.metric("Capacity Gap", "0 - Well Covered" if high_fit >= 1 else "Shortage")

# Filters
with st.expander("🔧 Filters"):
    min_score = st.slider("Minimum Suitability Score", 0, 10, 3)
    geo_only = st.checkbox("Show only Geo Matched")
    max_days = st.slider("Maximum Available in (Days)", 0, 100, 40)
    
    filtered = result_df[result_df['Suitability Score'] >= min_score]
    if geo_only:
        filtered = filtered[filtered['Geo Matched'] == 'Yes']
    
    def get_days(x):
        if str(x).strip().lower() == 'immediate':
            return 0
        try:
            return int(x)
        except:
            return 999
    filtered = filtered[filtered['Available in (Days)'].apply(get_days) <= max_days]

# Results Table
st.dataframe(
    filtered.style.background_gradient(subset=['Suitability Score'], cmap='RdYlGn')
    .format({'Suitability Score': '{:.0f}'}),
    use_container_width=True,
    hide_index=True
)

# Export Button
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Results as CSV",
    data=csv,
    file_name=f"{project_row['Project Name']}_resource_matching.csv",
    mime="text/csv"
)

st.success("✅ Matching Engine is live! Test with 'Humana Insurance' or create custom scenarios.")
