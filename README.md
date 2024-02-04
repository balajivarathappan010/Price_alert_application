                                               `Running the Project`
Step 1: Ensure MySQL server is running.
Step 2: Execute python app.py to start the Flask application.
Step 3: Access the endpoints using a REST client or API testing tool like Postman.

Endpoints

/api/login [POST]
Description: Endpoint to authenticate users.
Request Body: JSON object containing username and password.
Response:
200 OK with access token if authentication is successful.
401 Unauthorized if authentication fails.
/api/create [POST]
Description: Endpoint to fetch data from the Binance API, store it in the database, and trigger alerts.
Authorization: Requires JWT token obtained from /api/login endpoint.
Response:
200 OK with a message indicating the successful storage of data in the database.
/api/delete [DELETE]
Description: Endpoint to delete entries from the database where the price is less than 33000.
Authorization: Requires JWT token obtained from /api/login endpoint.
Response:
200 OK with a message indicating successful deletion.

Sending Alerts

The application sends email alerts when the price of Bitcoin crosses a certain threshold.

Alert Conditions:
If the price is above 33000, an email alert is sent.
If the price is below 33000, corresponding database entries are deleted, and a deletion event is logged.

SMTP Configuration:
SMTP Server: smtp.gmail.com
Port: 587
Username: Your Gmail username
Password: Your Gmail password
Email Template:
Subject: Price Alert
Body: The price of [current_price] is above 30000.
