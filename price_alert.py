from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import requests
import smtplib
import pandas as pd
import requests
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/authentication'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ooo'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

class Alerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    status = db.Column(db.String(50))

    def __init__(self, coin_name, current_price, status):
        self.coin_name = coin_name
        self.current_price = current_price
        self.status = status
class AlertSchema(ma.Schema):
    class Meta:
        fields = ('id','coin_name','current_price', 'status')

alert_schema = AlertSchema()
alerts_schema = AlertSchema(many=True)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'balajivarathappan@gmail.com'
SMTP_PASSWORD = 'jrhe xzou qnvj qbbo'
SENDER_EMAIL = 'balaji.v2020@vitstudent.ac.in'

def send_email(receiver_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
    
df = pd.DataFrame()
while True:
    response = requests.get('https://api.binance.com/api/v1/ticker/price?symbol=BTCUSDT')
    data = response.json()
    df = df.append(data, ignore_index=True)
    df.to_csv('btc.csv', index=False)
    if len(df)>=10:
            break
    
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username=='admin' and password=='balaji':
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token),200
    else:
        return jsonify({"message":"Invalid username or password"}), 401

@app.route('/api/create', methods=['POST'])
@jwt_required
def create_all():
    df = pd.read_csv('btc.csv')
    for _, row in df.iterrows():
        coin_name = row['symbol']
        old_price = row['price']
        current_price = float(old_price)
        if current_price > 33000:
            status = "Alert"
        else:
            status = "created"
        new_status = Alerts(coin_name, current_price, status)
        db.session.add(new_status)
        db.session.commit()
        if current_price > 33000:
            send_email(SENDER_EMAIL, 'Price Alert', f'The price of {current_price} is above 30000')
            status = 'triggered'
            trigger_status = Alerts(coin_name, current_price, status)
            db.session.add(trigger_status)
            db.session.commit()
    return jsonify({"message": "Data stored in database."})

@app.route('/api/delete',methods=['DELETE'])
@jwt_required
def delete_specific():
    df = pd.read_csv('btc.csv')
    for _, row in df.iterrows():
        price = float(row['price'])
        if price < 33000:
            Alerts.query.filter(Alerts.current_price == price).delete()
            db.session.commit()
    return jsonify({"msg":"deleted"})

if __name__=='__main__':
    app.run(debug=True, port=7000)
    
