\# Valora



An AI-assisted personal finance management (PFM) application built for the Indian financial context. Valora combines profession-based expense categorisation, automated transaction processing, budget management, expenditure analysis and spending forecasts in one app.



\## Why Valora



Digital payments have caused a surge in personal transaction volumes, but most finance apps lack personalisation, automated transaction management and decision support suited to Indian users. Valora addresses this with categories tailored to the user's profession and insights drawn from their own spending patterns.



\## Features



\- Profession-based expense categories (students, professionals, freelancers, business owners)

\- Transaction recording and automated transaction management

\- Budget setting and monitoring

\- Expenditure analysis with charts

\- Financial health metrics and category-wise risk evaluation

\- Future spending prediction based on historical spending



\## Tech stack



Python, Streamlit, FastAPI, SQLite, pandas, matplotlib, NumPy



\## Getting started



1\. Clone the repository:

&#x20;      git clone https://github.com/ascendify-core/VALORA.git

&#x20;      cd VALORA

2\. Install the dependencies:

&#x20;      pip install -r requirements.txt

3\. Create the database:

&#x20;      python init\_db.py

4\. Run the app:

&#x20;      streamlit run main.py



To run the REST API as well:



&#x20;   uvicorn api:app --reload



\## Research paper



Valora is described in a peer-reviewed conference paper:



Ambarish A, Anjali Satheesan C, Unni Krishnan S Kumar, Ansil Sajad K and Anand TK. "Valora: An AI-Powered Personal Financial Tracking Application." SHS Web of Conferences 237, 09006 (2026), CRMT 2026. https://doi.org/10.1051/shsconf/202623709006



\## Roadmap



\- Machine-learning-based prediction models

\- Mobile platform support



\## Authors



Dept of CSE (Data Science), JCET Ottapalam

