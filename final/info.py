import streamlit as st

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
st.header("About the Open Source Projects Community Project")

summarized_text = """
The project focuses on analyzing Reddit and GitHub data to explore user engagement, toxicity, and technology adoption in online communities. Key points include:
- Social media's influence on decisions.
- Managing open-source projects on web repository platforms.
- Collecting data from Reddit and GitHub, predicting toxicity.
- Exploring engagement and overall friendliness of online communities.
- Analyzing user adoption of different technologies.
- Research questions, objectives, and plans for an interactive dashboard.
- Tools to be used: Streamlit, Matplotlib, NLTK, Plotly, Wordcloud.
- Future work includes expanding to more technology stacks.
"""

st.markdown(summarized_text)

research_questions_summary = """
The proposed research questions aim to study user engagement patterns in online forums for aiding technology stack selection. Key questions include:
1. Assessing the friendliness of GitHub repositories and SubReddits.
2. Evaluating the popularity of technology stacks and issue resolution speed.
3. Determining if the analysis aids in deciding a technology stack.
"""
st.markdown("---")
st.markdown("### Data Sources")
st.write("""The data for this dashboard is collected from the following sources:
- [GitHub API](https://docs.github.com/en/rest)
- [Reddit API](https://www.reddit.com/dev/api/)
         """)

st.markdown("---")
st.markdown("### Technical Stacks Monitered")
st.write("""The dashboard currently monitors the following technical stacks on their github and reddit communities.""")
st.markdown("""
            * [Rust](https://www.rust-lang.org/)
            * [Go](https://golang.org/)
            * [Nix](https://nixos.org/)
            * [Kubernetes](https://kubernetes.io/)
            * [Swift](https://swift.org/)
            * [Flutter](https://flutter.dev/)
            * [TypeScript](https://www.typescriptlang.org/)
            """)
st.markdown("---")

# Streamlit app title and summarized content display
st.subheader('Proposed Research Questions')
st.markdown(research_questions_summary)

st.markdown("---")


future_work_summary = """
Future work could include expanding the analysis to more technology stacks for comparative assessments between different communities. 
This might require changes in the data collection system, considering API rate limits. However, it would be an interesting approach for the future.
"""
st.subheader('Future Work')
st.markdown(future_work_summary)

# add a made using section
st.markdown("---")
st.header("Made Using:")
tools = """
[![Streamlit](https://img.shields.io/badge/Streamlit-red?logo=Streamlit)](https://streamlit.io/) 
[![Python](https://img.shields.io/badge/Python-blue?logo=Python)](https://www.python.org/) 
[![Plotly](https://img.shields.io/badge/Plotly-orange?logo=Plotly)](https://plotly.com/) 
[![Matplotlib](https://img.shields.io/badge/Matplotlib-blue?logo=Matplotlib)](https://matplotlib.org/) 
[![NLTK](https://img.shields.io/badge/NLTK-green?logo=NLTK)](https://www.nltk.org/) 
[![Postgres](https://img.shields.io/badge/Postgres-blue?logo=Postgres)](https://www.postgresql.org/) 
[![Faktory](https://img.shields.io/badge/Faktory-red?logo=Faktory)](https://contribsys.com/faktory/) 
[![Reddit](https://img.shields.io/badge/Reddit-orange?logo=Reddit)](https://www.reddit.com/) 
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=GitHub)](https://github.com) 
[![ModerateHateSpeech](https://img.shields.io/badge/ModerateHateSpeech-red?logo=ModerateHateSpeech)](https://moderatehatespeech.com/) 
"""
st.markdown(tools)
st.markdown("---")
st.header("Made by:")
st.text("Akash Rasal")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Profile-green?logo=GitHub)](https://github.com/arasal2)")
st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=LinkedIn)](https://www.linkedin.com/in/akash-rasal-663953156/)")
st.text("Apoorv Yadav")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Profile-green?logo=GitHub)](https://github.com/ayadav16)")
st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=LinkedIn)](https://www.linkedin.com/in/yadavapoorv/)")

