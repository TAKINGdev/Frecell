import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Frecell', layout="wide")

st.title("📊 Frecell — Interactive Data Analysis Platform")
st.write("Upload, analyze, and visualize your datasets in seconds.")

tabs = st.tabs(['📥 Import Data', '🧪 Query Editor', '📈 Plot Designer'])

# Tab 1: CSV Upload
with tabs[0]:
    st.header("Upload Your CSV File")
    uploaded_file = st.file_uploader("Select a CSV file to begin", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df

        st.success("✅ File uploaded and loaded successfully.")

        row_limit = st.number_input(
            label="Number of rows to preview",
            min_value=1,
            max_value=df.shape[0],
            value=5,
            step=1,
            format="%d"
        )

        st.subheader(f"Preview (Top {row_limit} Rows)")
        st.dataframe(df.head(row_limit), use_container_width=True)

    elif "df" not in st.session_state:
        st.info("Please upload a CSV file to get started.")

# Tab 2: Pandas Code Execution
with tabs[1]:
    st.header("Pandas Query Editor")

    if "df" not in st.session_state:
        st.warning("CSV data not found. Please upload a file first.")
    else:
        query_code = st.text_area(
            "Write your pandas expression using the variable `df`:",
            height=100,
            placeholder="e.g. df[df['Age'] > 30]"
        )

        if st.button("▶️ Run Query"):
            try:
                local_env = {
                    "df": st.session_state.df.copy(),
                    "pd": pd
                }
                result = eval(query_code, {}, local_env)

                st.success("✅ Code executed successfully.")
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, use_container_width=True)
                else:
                    st.write(result)

            except Exception as e:
                st.error(f"❌ Execution Error: {e}")

# Tab 3: Plotting
with tabs[2]:
    st.header("Custom Plot Builder (Matplotlib)")

    if "df" not in st.session_state:
        st.warning("CSV data not found. Please upload a file first.")
    else:
        df = st.session_state.df
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            st.error("Your dataset has no numeric columns to plot.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("Select X Axis", numeric_cols)
            with col2:
                y_axis = st.selectbox("Select Y Axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)

            default_plot_code = f"""\
fig, ax = plt.subplots()
ax.plot(df["{x_axis}"], df["{y_axis}"])
ax.set_xlabel("{x_axis}")
ax.set_ylabel("{y_axis}")
ax.set_title("{y_axis} vs {x_axis}")
ax.grid(True)
"""

            custom_plot_code = st.text_area(
                "Write your custom matplotlib code (you can use `df`, `plt`, `fig`, `ax`):",
                value=default_plot_code,
                height=200
            )

            if st.button("📊 Generate Plot"):
                try:
                    exec_env = {
                        "df": df,
                        "plt": plt,
                        "pd": pd
                    }
                    exec(custom_plot_code, exec_env)
                    st.pyplot(exec_env.get("fig", plt.gcf()))
                except Exception as e:
                    st.error(f"❌ Plotting Error: {e}")
