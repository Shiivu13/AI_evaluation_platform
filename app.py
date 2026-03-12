import streamlit as st
import pandas as pd
from core.crud import (
    get_all_experiments, create_experiment,
    get_variants_for_experiment, create_variant,
    get_test_cases_for_experiment, add_test_case,
    get_evaluation_runs_for_variant, get_results_for_run
)
from core.db import init_db
from core.runner import run_evaluation_for_variant

# Ensure DB is initialized
init_db()

st.set_page_config(page_title="AI Eval Platform", layout="wide")

st.title("🧪 AI Experiment Evaluation Platform")

# Sidebar: Select Experiment
st.sidebar.header("Experiments")
experiments = get_all_experiments()

exp_options = {exp['name']: exp['id'] for exp in experiments}
selected_exp_name = st.sidebar.selectbox("Select Experiment", list(exp_options.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("Create New Experiment")
with st.sidebar.form("new_exp_form"):
    new_exp_name = st.text_input("Name")
    new_exp_desc = st.text_area("Description")
    if st.form_submit_button("Create Experiment"):
        if new_exp_name:
            create_experiment(new_exp_name, new_exp_desc)
            st.rerun()

if selected_exp_name:
    exp_id = exp_options[selected_exp_name]
    
    tab1, tab2, tab3 = st.tabs(["Test Cases", "Variants & Runs", "Analytics"])
    
    with tab1:
        st.header("Test Cases")
        test_cases = get_test_cases_for_experiment(exp_id)
        if test_cases:
            df_tc = pd.DataFrame(test_cases)[['id', 'input_data', 'context', 'expected_output']]
            st.dataframe(df_tc, use_container_width=True)
        else:
            st.info("No test cases yet. Add some below.")
            
        with st.expander("➕ Add Test Case"):
            with st.form("new_tc_form"):
                tc_input = st.text_area("Input Prompt Data (e.g. user question)")
                tc_context = st.text_area("Context (optional ground truth or documents)")
                tc_expected = st.text_area("Expected Output / Reference (optional)")
                if st.form_submit_button("Save Test Case"):
                    add_test_case(exp_id, tc_input, tc_expected, tc_context)
                    st.success("Test case added!")
                    st.rerun()

    with tab2:
        st.header("Prompt Variants")
        variants = get_variants_for_experiment(exp_id)
        if variants:
            for var in variants:
                with st.expander(f"Variant: {var['name']} (Model: {var['model_name']})", expanded=False):
                    st.code(var['prompt_template'], language="text")
                    st.caption(f"Temperature: {var['temperature']}")
                    last_runs = get_evaluation_runs_for_variant(var['id'])
                    
                    if st.button(f"▶ Run Evaluation for '{var['name']}'", key=f"run_{var['id']}"):
                        with st.spinner("Running evaluations..."):
                            run_evaluation_for_variant(var['id'])
                        st.success("Run completed!")
                        st.rerun()
                    
                    if last_runs:
                        st.markdown("**Recent Runs:**")
                        runs_df = pd.DataFrame(last_runs)[['id', 'status', 'created_at', 'completed_at']]
                        st.dataframe(runs_df, hide_index=True)
                        
                        latest_run_id = last_runs[0]['id']
                        if st.button("View Latest Run Results", key=f"view_{latest_run_id}"):
                            st.session_state['view_run'] = latest_run_id
                            st.rerun()
        else:
            st.info("No variants created yet.")
            
        with st.expander("➕ Create New Variant"):
            with st.form("new_variant_form"):
                v_name = st.text_input("Variant Name", placeholder="e.g. Zero-shot v1")
                v_model = st.selectbox("LLM Model", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"])
                v_temp = st.slider("Temperature", 0.0, 1.0, 0.7)
                v_prompt = st.text_area("Prompt Template", "Respond to the following input: {{input}}\nContext: {{context}}")
                st.caption("Use {{input}} and {{context}} as placeholders.")
                
                if st.form_submit_button("Save Variant"):
                    create_variant(exp_id, v_name, v_prompt, v_model, v_temp)
                    st.success("Variant saved!")
                    st.rerun()
                    
    with tab3:
        st.header("📈 Evaluation Results")
        view_run_id = st.session_state.get('view_run')
        if view_run_id:
            st.subheader(f"Results for Run ID: {view_run_id}")
            results = get_results_for_run(view_run_id)
            if results:
                df_results = pd.DataFrame(results)
                
                # Aggregate Scores
                agg_scores = df_results.groupby('metric_name')['score'].mean().reset_index()
                
                st.markdown("### 📊 Average Metric Scores")
                # Create dynamic metric cards
                cols = st.columns(len(agg_scores))
                for i, row in agg_scores.iterrows():
                    metric = row['metric_name']
                    score = row['score']
                    
                    # Determine color mapping for UI (mock red/yellow/green feel)
                    delta_color = "normal"
                    if score >= 0.8:
                        color_prefix = "🟢"
                    elif score >= 0.5:
                        color_prefix = "🟡"
                    else:
                        color_prefix = "🔴"
                        
                    cols[i].metric(label=f"{color_prefix} {metric}", value=f"{score:.2f}")
                
                st.markdown("---")
                st.markdown("### 🔍 Raw Results & Judge Rationale")
                
                # Styled dataframe
                st.dataframe(
                    df_results[['test_case_id', 'metric_name', 'score', 'rationale', 'evaluator_type']],
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning("No results found for this run. Perhaps test cases were missing.")
                
            if st.button("Close View"):
                del st.session_state['view_run']
                st.rerun()
        else:
            st.info("Trigger an evaluation or select 'View Latest Run Results' from the Variants tab.")

else:
    st.info("Please select or create an experiment from the sidebar.")
