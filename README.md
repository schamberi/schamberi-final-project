API Setup 
This README provides step-by-step instructions for setting up and using the API for this project. Follow these guidelines to ensure a smooth installation process.

Installation
Clone the Repository:
git clone schamberi/final-project
cd djangoassignment


On Windows:
menv\Scripts\activate
On Unix or MacOS:
source menv/bin/activate

Install Dependencies:
pip install -r requirements.txt
Apply Migrations:
python manage.py migrate

To runtheserver: py manage.py runserver

Data Upload
To upload data to the API, utilize the provided endpoint:
Endpoint: /cashflow/upload/
Method: POST
Upload Excel files with the following names to the static_data directory:
trades.xlsx for trades data
cash_flows.xlsx for cash flow data
Other API Endpoints
Realized Amount
Endpoint: /cashflow/realized-amount/<str:loan_id>/<str:reference_date>/
Method: GET
Provide loan_id and reference_date in the URL to retrieve the realized amount.
Gross Expected Amount
Endpoint: /cashflow/gross-amount/<str:loan_id>/<str:reference_date>/
Method: GET
Provide loan_id and reference_date in the URL to retrieve the gross expected amount.
Remaining Invested Amount
Endpoint: /cashflow/remaining-invested-amount/<str:loan_id>/<str:reference_date>/
Method: GET
Provide loan_id and reference_date in the URL to retrieve the remaining invested amount.
Closing Date
Endpoint: /cashflow/closing-date/<str:loan_id>/<str:reference_date>/
Method: GET
Provide loan_id and reference_date in the URL to retrieve the closing date.
Invested Amount
Endpoint: /cashflow/invested-amount/<str:loan_id>/<str:reference_date>/
Method: GET
Provide loan_id and reference_date in the URL to retrieve the invested amount.
Trades List
Endpoint: /cashflow/trades-list/
Method: GET
Retrieve a list of trades from the API.
Cashflow List
Endpoint: /cashflow/cashflow-list/
Method: GET
Retrieve a list of cashflows from the API.

Container Image Creation and Activation on the terminal with the virtual enviornment activated
docker composer up --build, make sure to have docker installed on your machine
