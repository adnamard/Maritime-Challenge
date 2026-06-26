# 🚢 HorizonMaritime: Executive Operations Analytics & Terminal Optimization

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_STREAMLIT_SHARE_LINK_HERE)
![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An executive-level decision-support tool and interactive dashboard designed to identify global maritime operational bottlenecks, analyze the macroeconomic impact of the 2021 Suez Canal crisis, and provide data-driven strategies to reduce cargo movement duration (`move_duration`) by **15%**.

This project was developed as a competitive submission for the **Maritime Operations Datathon**.

---

## 📌 Business Case & Objectives

Following the 2021 Suez Canal disruption, global supply chains faced unprecedented bottlenecks. This analytics solution evaluates maritime cargo movement data (2021–2024) across 4 regional hubs (EMEA, APAC, AMER, LATAM) and 50 terminals to address four critical executive questions:

1. **Where are our operational bottlenecks?** Identifying underperforming terminals and vessel categories.
2. **How can we optimize terminal allocation?** Tactical recommendations to hit the targeted 15% reduction in cargo movement times.
3. **What was the true impact of the 2021 Suez disruption?** Quantifying the macro-shock to isolate structural inefficiencies from temporary disruptions.

---

## 📊 Key Insights & Statistical Framework

Our rigorous exploratory data analysis (EDA) and statistical hypothesis testing yielded the following core findings:

* **The Suez Shock (+15%):** The 2021 Suez Canal disruption caused a statistically significant ~15% surge in global `move_duration`.
* **Ground Zero (EMEA):** Statistical testing confirmed that the EMEA region sustained the most severe and prolonged operational degradation.
* **Debunking the Surge Hypothesis:** Contrary to industry assumptions, hypothesis testing showed no strong empirical evidence of a significant post-Suez cargo volume surge; the bottleneck was purely velocity-driven.
* **The Noise vs. The Signal:** Operational variables such as *vessel age, vessel category, shift timing, and container volume* showed negligible influence on overall movement duration. Performance stability relies heavily on **geographic location** and **terminal-specific efficiency**.

---

## 🛠️ Tech Stack & Architecture

* **Core Analytics:** Python, Pandas, NumPy, SciPy (Hypothesis Testing)
* **Dashboard Interface:** Streamlit (Custom Premium/Minimalist Theme)
* **Data Visualization:** Plotly Express / Altair (Configured for McKinsey/BCG executive styling)
* **Production Architecture:** Modular structural design optimized for layout separation, state management, and memory caching (`@st.cache_data`).