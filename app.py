from flask import Flask, render_template, request, url_for, jsonify, session
from flask_restx import Api, Resource, fields, reqparse
from dateutil import parser as date_parser
from flask import Flask, render_template, request, url_for, jsonify
from passlib.hash import sha256_crypt
import os, hashlib, base64
from hashlib import sha256
from functools import wraps
import io
from model.User import User
from model.UserLanguage import UserLanguage
from model.Club import Club
from model.ClubLanguage import ClubLanguage
from model.ClubCategory import ClubCategory
from model.ClubMember import ClubMember
from model.ClubEvent import ClubEvent
from model.EventAttendee import EventAttendee
from model.Post import Post
from model.UserPost import UserPost
from model.PostImage import PostImage
from model.PostReact import PostReact
from model.Category import Category
from model.UserCategory import UserCategory
from model.UserSuggestCategory import UserSuggestCategory
from model.Group import Group
from model.GroupCategories import GroupCategories
from model.Event import Event
from model.UserLeaveClub import UserLeaveClub
from model.CommentPost import CommentPost
from model.Language import Language
from model.Payment import Payment
from model.EmailVerify import EmailVerify
from model.LocalNews import LocalNews
from model.UserConnect import UserConnect
from model.UserPref import UserPref
from model.Country import Country
from model.Timezone import Timezone
from model.GeoCity import GeoCity
from model.UserSuggest import UserSuggest
from config import Config
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
import os, hashlib, base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from util.SendEmail import send_email
import jwt
import secrets
import qrcode
import pyotp
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt
from flask_jwt_extended import decode_token
import stripe
stripe.api_key = ''


app = Flask(__name__)
api = Api(app, version='1.0', title='Hobbymeet API',description='API Documentation')
#disable the documentation api = Api(app, doc=False)
app.config.from_object(Config)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
app.config['RATELIMIT_HEADERS_ENABLED'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
limiter = Limiter(get_remote_address, app=app, default_limits=["1000 per day", "100 per hour"])

server_domain = app.config['SERVER_DOMAIN_PROD']

if app.config['IS_DEV']:
    server_domain = app.config['SERVER_DOMAIN_DEV']
elif app.config['IS_TEST']:
    server_domain = app.config['SERVER_DOMAIN_TEST']
    
profile_images_folder = os.path.join(os.getcwd(), 'static', app.config['PROFILE_IMAGES_FOLDER'])
if not os.path.exists(profile_images_folder):
    os.makedirs(profile_images_folder)


post_images_folder = os.path.join(os.getcwd(), 'static', app.config['POST_IMAGES_FOLDER'])
if not os.path.exists(post_images_folder):
    os.makedirs(post_images_folder)

user_post_images_folder = os.path.join(os.getcwd(), 'static', app.config['USER_POST_IMAGES_FOLDER'])
if not os.path.exists(user_post_images_folder):
    os.makedirs(user_post_images_folder)

server_domain = app.config['SERVER_DOMAIN_PROD']

if app.config['IS_DEV']:
    server_domain = app.config['SERVER_DOMAIN_DEV']
elif app.config['IS_TEST']:
    server_domain = app.config['SERVER_DOMAIN_TEST']

profile_images_folder = os.path.join(os.getcwd(), 'static', app.config['PROFILE_IMAGES_FOLDER'])
if not os.path.exists(profile_images_folder):
    os.makedirs(profile_images_folder)

post_images_folder = os.path.join(os.getcwd(), 'static', app.config['POST_IMAGES_FOLDER'])
if not os.path.exists(post_images_folder):
    os.makedirs(post_images_folder)
    
category_images_folder = os.path.join(os.getcwd(), 'static', app.config['CATEGORY_IMAGES_FOLDER'])
if not os.path.exists(category_images_folder):
    os.makedirs(category_images_folder)


group_images_folder = os.path.join(os.getcwd(), 'static', app.config['GROUP_IMAGES_FOLDER'])
if not os.path.exists(group_images_folder):
    os.makedirs(group_images_folder)

qr_images_folder = os.path.join(os.getcwd(), 'static', app.config['QR_IMAGES_FOLDER'])
if not os.path.exists(qr_images_folder):
    os.makedirs(qr_images_folder)

news_related_folder = os.path.join(os.getcwd(), 'static', app.config['NEWS_RELATED_FOLDER'])
if not os.path.exists(news_related_folder):
    os.makedirs(news_related_folder)

events_related_folder = os.path.join(os.getcwd(), 'static', app.config['EVENT_IMAGES_FOLDER'])
if not os.path.exists(events_related_folder):
    os.makedirs(events_related_folder)

clubs_related_folder = os.path.join(os.getcwd(), 'static', app.config['CLUB_IMAGES_FOLDER'])
if not os.path.exists(clubs_related_folder):
    os.makedirs(clubs_related_folder)

def hash_password(password):
    return sha256_crypt.using(rounds=1000).hash(password)

#Payment Related Stripe codes start
def calculate_tax(items, currency, address_line1, city, state, postal_code, country_code, address_source):
    tax_calculation = stripe.tax.Calculation.create(
        currency= currency,
        customer_details={
            "address": {
                "line1": address_line1,
                "city": city,
                "state": state,
                "postal_code": postal_code,
                "country": country_code,
            },
            "address_source": address_source,
        },
        line_items=list(map(build_line_item, items)),
    )

    return tax_calculation

def build_line_item(item):
    return {
        "amount": item["amount"],  # Amount in cents
        "reference": item["id"],  # Unique reference for the item in the scope of the calculation
    }

# Securely calculate the order amount, including tax
def calculate_order_amount(items, tax_calculation):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total with any exclusive taxes on the server to prevent
    # people from directly manipulating the amount on the client
    order_amount = 0
    for item in items:
        order_amount += item["amount"]
    order_amount += tax_calculation['tax_amount_exclusive']
    return order_amount


#Payment Related Stripe codes end

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = User.isTokenBlackListed(jti)

    return token is not None


@jwt.expired_token_loader
def expired_token_callback(var1,  var2):
    request.form
    return {"message": "Expired Token"}, 401


@jwt.revoked_token_loader
def revoked_token_callback():
    request.form
    return {"message": "Revoked Token"}, 401
# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            if user_id == None:
                return {"message": "Invalid Access Token"}, 401
            current_user = User.getUser(user_id)
            kwargs['current_user'] = current_user

        except Exception as e:
            return {"message": "Erorr getting user info"}, 500
        return f(*args, **kwargs)
    return decorator

def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):  
            user_id = get_jwt_identity()
            try:    
                current_user = User.user_details(user_id)  
                kwargs['current_user'] = current_user

                if required_roles and current_user['user_role'] not in required_roles:
                    return {"message": "Unauthorized"}, 403
            except Exception as e:
                return {"message": "Error: {}".format(str(e))}, 500

            return f(*args, **kwargs)
        return wrapper
    return decorator

def generate_OTP():
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    return totp.now()

def generate_ticket_number():
    ticket_length = 10  
    ticket_number = secrets.token_hex(ticket_length // 2).upper() 
    return ticket_number

def generate_qr_code(data, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

def parse(value):
    if not value:
        return []
    return [lang.strip() for lang in value.split(',')]

#Payment Gateway Stripe 
parserStripePayment = reqparse.RequestParser()
parserStripePayment.add_argument('event_id', type=int, required=True, help='Items in the cart', location='json', )
parserStripePayment.add_argument('number_of_tickets', type=int, required=True, help='Items in the cart', location='json', )
parserStripePayment.add_argument('address', type=dict, required=True, help='Customer address', location='json')
parserStripePayment.add_argument('currency', type=str, required=True, help='Currency', location='json')

payment_model_stripe = api.model('PaymentRequestBody', {
    'items': fields.List(fields.Nested(api.model('item',{
        'id': fields.String(required=True, description='Event ID', example='E42T0000001'),
        'amount': fields.List(fields.Integer, required=True, description='Amount in cents', example=30000)
    })), required=True, description='Item list that customer bought.', example=[{
        'id': 'E42T0000001',
        'amount': 30000
    }, {
        'id': 'E42T0000002',
        'amount': 35000
    }]),
    'address': fields.Nested(api.model('address',{
        'line1': fields.String(required=True, description='Address Line 1', example='23 Lorence Avenue'),
        'city': fields.String(required=True, description='City name', example='George Town'), 
        'state': fields.String(required=True, description='State', example='New Maxico'), 
        'postal_code': fields.String(required=True, description='Postal Code', example="10920"), 
        'country_code': fields.String(required=True, description='Country Code', example='US'), 
        'address_source': fields.String(required=True, description='Address Source', example='Shipping'), 

    }), required=True, description='Customer Address', example={
        'line1': '23 Lorence Avenue',
        'city': 'George Town', 
        'state': 'New Maxico', 
        'postal_code': "10920", 
        'country_code': 'US', 
        'address_source': 'Shipping'
    }),
    'currency': fields.String(required=True, description='Currency', example='DKK')
})

@api.route('/create-payment-intent')
class CreatePayment(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserStripePayment)
    def post(self,**kwargs):
        try:
            args = parserStripePayment.parse_args()
            current_user = kwargs['current_user']
            user_id = current_user['id']
            event_id = args['event_id']
            number_of_tickets = args['number_of_tickets']
            event_cost = Event.get_event_cost(event_id).get('cost') 
            client_ip = request.remote_addr

            if not event_cost:
                event_cost = 0
            
            amount_total = (event_cost * number_of_tickets)
            nett_amount = ( amount_total / 125 ) * 100
            # nett_amount = all_total * 0.8
            tax = amount_total - nett_amount

            event_cost_cents = int(event_cost * 100)

            #Invoice Number Generation
            invoice_number = Payment.get_next_invoice_number()

            #Ticket Number Generation
            tickets = []
            for _ in range(number_of_tickets):
                # Generate a ticket number
                new_ticket_number = generate_ticket_number()

                # Check if the ticket number already exists
                existing_ticket = Payment.get_next_ticket_number(new_ticket_number)

                if existing_ticket:
                    # If ticket number already exists, generate a new one
                    while existing_ticket:
                        new_ticket_number = generate_ticket_number()
                        existing_ticket = Payment.get_next_ticket_number(new_ticket_number)

                

                qr_data = f"Ticket Number: {new_ticket_number}, User ID: {user_id}, Event ID: {event_id}"
                qr_image_path = os.path.join(qr_images_folder, f"ticket_{new_ticket_number}.png")
                generate_qr_code(qr_data, qr_image_path)

                tickets.append({
                    "ticket_number": new_ticket_number,
                    "qr_image": f"ticket_{new_ticket_number}.png"})

            if tickets: 
                items = []
                for ticket in tickets:
                    item = {
                        'id': ticket['ticket_number'],
                        'amount': event_cost_cents 
                    }
                    items.append(item)

                address = args['address']
                print(items)
                print(address)
                # Create a Tax Calculation for the items being sold
                tax_calculation = calculate_tax(items, 'dkk', address['line1'], address['city'], address['state'], address['postal_code'],
                                                address['country_code'], address['address_source'])
                print(tax_calculation)

                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=calculate_order_amount(items, tax_calculation),
                    currency='dkk',
                    # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
                    automatic_payment_methods={
                        'enabled': True,
                    },
                    metadata={
                    'tax_calculation': tax_calculation['id']
                    },
                )
                print(intent)
                payment_intent_id = intent.id
                NewInvoice = Payment.addPayment(invoice_number, payment_intent_id, user_id, event_id, client_ip, address['line1'], address['city'], address['state'], address['postal_code'],
                                                        address['country_code'], address['address_source'], number_of_tickets, amount_total, event_cost, nett_amount, tax)

                if NewInvoice:
                    addTicket = Payment.addTicket(invoice_number, tickets)

                    if addTicket:
                        return jsonify({
                            'clientSecret': intent['client_secret']
                        })
        except Exception as e:
            print(f"Error in Creating payment: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 500

# Invoke this method in your webhook handler when `payment_intent.succeeded` webhook is received
def handle_payment_intent_succeeded(payment_intent):
    # Create a Tax Transaction for the successful payment 
    stripe.tax.Transaction.create_from_calculation(
        calculation=payment_intent['metadata']['tax_calculation'],
        reference="myOrder_123",  # Replace with a unique reference from your checkout/order system
    )

#Payment Gateway Stripe end

#Payment Web Hook, to listen to stripe events 
    
@api.route('/webhook')
class ReceiveStripeEvent(Resource):
    @api.expect()
    def post(self,):
        payload = request.json
        print(payload)
        event = None
        try:
            event = stripe.Event.construct_from(
                payload, stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            print(e)
            return {"success": False, "message": "Invalid Value"}, 400

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object # contains a stripe.PaymentIntent
            payment_intent_id = payment_intent['id']
            print(payment_intent_id)
            invoice_result = Payment.getInvoiceDetails(payment_intent_id)
            invoice_number = invoice_result['invoice_number']
            amount = invoice_result['invoice_amount']
            user_id = invoice_result['user_id']
            event_id = invoice_result['event_id']
            Payment.updatePaidStatus(payment_intent_id, invoice_number, amount)
            tickets = Payment.getTickets(invoice_number)
            for ticket in tickets:
                EventAttendee.addEventAttendee(event_id, user_id, ticket['ticket_number'])
            print('PaymentIntent was successful!')
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object # contains a stripe.PaymentMethod
            print('PaymentMethod was attached to a Customer!')
        else:
            print('Unhandled event type {}'.format(event.type))

        return {"status": "success"}, 200

#Register Route

parserRegister = reqparse.RequestParser()
parserRegister.add_argument('email', type=str, required=True, help='Email is required', location='json')
parserRegister.add_argument('username', type=str, required=True, help='Username is required', location='json')
parserRegister.add_argument('password', type=str, required=True, help='Password is required', location='json')
parserRegister.add_argument('dob', type=lambda x: date_parser.parse(x).date() if isinstance(x, str) else x, required=True, help='Date of birth is required (format: %Y-%m-%d)', location='json')
parserRegister.add_argument('phone_number', type=str, required=True, help='Phone number is required', location='json')
parserRegister.add_argument('gender', type=str, required=True, choices=('male', 'female'), help='Gender is required (choices: male, female)', location='json')
parserRegister.add_argument('gender_others', type=str, required=False, help='Gender others is string input', location='json')
parserRegister.add_argument('aboutme', type=str, required=True, help='Provide a brief description about yourself', location='json')
parserRegister.add_argument('country', type=str, required=True, help='Country is required', location='json')
parserRegister.add_argument('preferred_language', type=str, required=True, help='Preferred language is required', location='json')
parserRegister.add_argument('languages',type=list, required=True, help='List of languages is required', location='json')
parserRegister.add_argument('profile_image', type=str, required=True, help='Profile Image is required', location='json')

@api.route('/register')  
class RegisterResource(Resource):
    @api.expect(parserRegister)
    def post(self):
        args = parserRegister.parse_args()
        email = args['email']
        username = args['username']
        password = args['password']
        dob = args['dob'] 
        phone_number = args['phone_number']
        gender = args['gender']
        gender_others = args['gender_others']
        aboutme = args['aboutme']
        country = args['country']
        preferred_language = args['preferred_language']
        languages = args['languages']
        profile_image = args['profile_image']

        try:
            language_ids = list(map(int, languages))
        except:
            return {"success": False, "message": "Language List must be integers"}, 400
                
        hashed_password = hash_password(password)
        if User.user_exists(email):
            return {"success": False, "message": "Email already exists"}, 400
        
        image_data = base64.b64decode(profile_image)         
        filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
        file_path = os.path.join(profile_images_folder, filename)

        with open(file_path, 'wb') as file:
            file.write(image_data)

        result = User.register(email, username, hashed_password, dob, phone_number, country, preferred_language, gender, gender_others, aboutme, filename)

        userData = {
            "email": result['email'],
            "username": result['username'],
            "dob": str(result['dob']),
            "phone_number":result['phone_number'],
            "gender": result['gender'],
            "gender_others": result['gender_others'],
            "aboutme" : result['aboutme'],
            "country": result['country'],
            "preferred_language": result['preferred_language'],
            "profile_image": f"{server_domain}static/{app.config['PROFILE_IMAGES_FOLDER']}/{result['profile_image']}"
        }
       
        refresh_token = create_refresh_token(identity=result['id'])
        decoded_rt = decode_token(refresh_token)
        refresh_token_jti = decoded_rt["jti"]
        refresh_token_ttype =decoded_rt["type"]
        User.addToken(refresh_token_jti, refresh_token_ttype, result['id'], "")

        access_token = create_access_token(identity=result['id'], additional_claims = {"rtjti" : refresh_token_jti}, fresh=True)
        decoded_at = decode_token(access_token)
        access_token_jti = decoded_at["jti"]
        access_token_ttype = decoded_at["type"]
        User.addToken(access_token_jti, access_token_ttype, result['id'], refresh_token_jti)


        added_languages = UserLanguage.addUserLanguage(result['id'], language_ids)


        send_email('contactus@vasthive.fo', result['email'],
                    'Hobby Meet Registration',
                    '<strong>Hobby Meet Registration Successful</strong>')

        if result:
            return { "user": userData, "languages": added_languages, "token" : access_token, "refresh": refresh_token}, 200
        else:
           return {"success": False, "message": "invalid request format"}, 400


        
##### Login ##### 

parserLogin = reqparse.RequestParser()
parserLogin.add_argument('email', type=str, required=True, help='Email is required',  location='json')
parserLogin.add_argument('entered_password', type=str, required=True, help='Password is required',  location='json')

@api.route('/login')
class LoginResource(Resource):
    @api.expect(parserLogin)
    @limiter.limit("4 per minute;30 per hour;60 per day")
    def post(self):
        args = parserLogin.parse_args()
        email = args['email']
        entered_password = args['entered_password']
        result = User.login(email)
        languages = UserLanguage.getUserLanguage(result['id'])

        if result:
            userData = {
                "email": result['email'],
                "username": result['username'],
                "dob": str(result['dob']),
                "phone_number":result['phone_number'],
                "gender": result['gender'],
                "gender_others": result['gender_others'],
                "country": result['country'],
                "preferred_language": result['preferred_language'],
                "profile_image": f"{server_domain}static/{app.config['PROFILE_IMAGES_FOLDER']}/{result['profile_image']}"
            }

            hashed_password = result['password']
            if sha256_crypt.verify(entered_password, hashed_password):
                refresh_token = create_refresh_token(identity=result['id'])
                decoded_rt = decode_token(refresh_token)
                refresh_token_jti = decoded_rt["jti"]
                refresh_token_ttype =decoded_rt["type"]
                User.addToken(refresh_token_jti, refresh_token_ttype, result['id'], "")

                access_token = create_access_token(identity=result['id'], additional_claims = {"rtjti" : refresh_token_jti}, fresh=True)
                decoded_at = decode_token(access_token)
                access_token_jti = decoded_at["jti"]
                access_token_ttype = decoded_at["type"]
                User.addToken(access_token_jti, access_token_ttype, result['id'], refresh_token_jti)

                return {"message": "Login successful",  "user": userData, "languages": languages, "token" : access_token, "refresh": refresh_token}, 200


            else:
                return {"message": "Email or Password incorrect"}, 400
        else:
            return {"message": "Email or Password incorrect"}, 400
    
##### Refresh Token #####
@api.route("/refresh")
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        rtjti = get_jwt()["jti"]
        #invalidate previous refresh token
        User.InvalidateRefreshToken(rtjti)

        #Create new refresh token
        refresh_token = create_refresh_token(identity=identity)
        decoded_at = decode_token(refresh_token)
        refresh_token_jti = decoded_at["jti"]
        refresh_token_ttype = decoded_at["type"]
        User.addToken(refresh_token_jti, refresh_token_ttype, identity, "")

        #Create new access token
        access_token = create_access_token(identity=identity, additional_claims = {"rtjti" : refresh_token_jti}, fresh=False)
        decoded_at = decode_token(access_token)
        access_token_jti = decoded_at["jti"]
        access_token_ttype = decoded_at["type"]
        User.addToken(access_token_jti, access_token_ttype, identity, refresh_token_jti)
        
        if access_token:
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        else: 
            return {"message" : "Something went wrong!"}, 500
        
##### Logout ##### 
@api.route("/logout")
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        token = get_jwt()
        accesstoken_jti = token["jti"]
        
        refresh_token_jti = token["rtjti"]
        User.invalidateTokens([accesstoken_jti, refresh_token_jti])
        return {"message": "Successfully Logged out."}, 200


##### Update User ##### 
parserUpdateUser = reqparse.RequestParser()
parserUpdateUser.add_argument('aboutme', type=str, help='aboutme', location='json')
parserUpdateUser.add_argument('country', type=str, help='country', location='json')
parserUpdateUser.add_argument('preferred_language', type=str, help='preferred_language', location='json')
parserUpdateUser.add_argument('languages', type=list, help='List of languages is required', location='json')
parserUpdateUser.add_argument('profile_image', type=str, help='Profile Image is required', location='json')

@api.route('/user/update')
class UpdateUserResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUpdateUser)
    def post(self, *args, **kwargs):
        args = parserUpdateUser.parse_args()
        aboutme = args['aboutme']
        country = args['country']
        preferred_language = args['preferred_language']
        language_ids = args['languages']
        current_user = kwargs['current_user']
        profile_image = args['profile_image']

        filename = ""

        if profile_image != "" and profile_image != None: 
            image_data = base64.b64decode(profile_image)         
            filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
            file_path = os.path.join(profile_images_folder, filename)

            with open(file_path, 'wb') as file:
                file.write(image_data)
        filename = filename if filename is not None and filename != "" else None
        isUpdated = User.updateUser(current_user['id'], preferred_language, country, aboutme, filename)

        if isUpdated:
            updatedLanguages = []
            if language_ids is not None:
                try:
                    languages = list(map(int, language_ids))
                except:
                    return {"success": False, "message": "Language List must be integers"}, 400
                UserLanguage.deleteUserLanguage(current_user['id'])

                updatedLanguages = UserLanguage.addUserLanguage(current_user['id'], languages)

            isUpdated_json = isUpdated.copy()  # Avoid modifying original data

            # Convert date objects to strings

            isUpdated_json['created_at'] = str(isUpdated_json['created_at'])
            isUpdated_json['dob'] = str(isUpdated_json['dob'])
            isUpdated_json['profile_image'] = f"{server_domain}static/{app.config['PROFILE_IMAGES_FOLDER']}/{isUpdated_json['profile_image']}"
 
            return {"message": "User information updated successfully", "languages": updatedLanguages, "user": isUpdated_json}, 200
        else:
            return {"message": "User Not Found"}, 404
        
##### Check Email ##### 
parserCheckEmail = reqparse.RequestParser()
parserCheckEmail.add_argument('email', type=str, required=True, help='Email is required')

@api.route('/check-email')  
class CheckEmailResource(Resource):
    @api.expect(parserCheckEmail)
    def post(self):
        args = parserCheckEmail.parse_args()
        email = args['email']

        isExist = User.user_exists(email)

        if isExist:
            return {"user": True}, 200
        else:
            return {"user": False}, 400


##### Verify Email || Generate OTP ##### 
        
parserVerifyEmail = reqparse.RequestParser()
parserVerifyEmail.add_argument('email', type=str, required=True, help='Email is required',  location='json')

@api.route('/verify_email')  
class VerifyEmailResource(Resource):
    @api.expect(parserVerifyEmail)
    def post(self):
        args = parserVerifyEmail.parse_args()
        email = args['email']

        if not email:
            return {"success" : False, 'message' : 'Email address is required'}, 400
        
        email_exist = User.user_exists(email)

        if email_exist:
            return {"success" : False, 'message' : 'Email address already exists'}, 400

        otp = generate_OTP()

        hashed_otp = sha256_crypt.hash(otp)

        expires_at = datetime.now() + timedelta(minutes=5)

        save_verification = EmailVerify.save_otp_email( email, hashed_otp, expires_at, 0 )

        if save_verification:
            send_email('contactus@vasthive.fo', email,
                    'Verification Code',
                    """
                        <p>Please use the verification code below to sign in.</p>
                        <p><strong>{otp}</strong></p>
                        <p>If you didn't request this, you can ignore this email.</p>
                        <p>Thanks,<br/>Hobby Meet Team</p>
                    """.format(otp=otp))

            return {"success" : True, "message" : "An OTP has been sent to your email address.", "email" : save_verification}, 200   
        else:
            return {"success" : False, "message" : "Failed to generate OTP."}, 400

##### Verify Email #####
parserVerifyEmailReset = reqparse.RequestParser()
parserVerifyEmailReset.add_argument('email', type=str, required=True, help='Email is required',  location='json')

@api.route('/verify_email_reset')  
class VerifyEmailResetResource(Resource):
    @api.expect(parserVerifyEmailReset)
    def post(self):
        args = parserVerifyEmailReset.parse_args()
        email = args['email']

        if not email:
            return {"success" : False, 'message' : 'Email address is required'}, 400
        
        email_exist = User.user_exists(email)

        if email_exist:
            otp = generate_OTP()

            hashed_otp = sha256_crypt.hash(otp)

            expires_at = datetime.now() + timedelta(minutes=5)

            save_verification = EmailVerify.save_otp_email( email, hashed_otp, expires_at, 0 )

            if save_verification:
                send_email('contactus@vasthive.fo', email,
                        'Verification Code',
                        """
                            <p>Please use the verification code below to sign in.</p>
                            <p><strong>{otp}</strong></p>
                            <p>If you didn't request this, you can ignore this email.</p>
                            <p>Thanks,<br/>Hobby Meet Team</p>
                        """.format(otp=otp))

                return {"success" : True, "message" : "An OTP has been sent to your email address.", "email" : save_verification}, 200   
            else:
                return {"success" : False, "message" : "Failed to generate OTP."}, 400

##### Verify OTP ##### 
        
parserVerifyOTP = reqparse.RequestParser()
parserVerifyOTP.add_argument('email', type=str, required=True, help='Email is required',  location='json')
parserVerifyOTP.add_argument('otp', type=str, required=True, help='OTP',  location='json')

@api.route('/verify_otp')  
class VerifyOTPResource(Resource):
    @api.expect(parserVerifyOTP)
    def post(self):
        args = parserVerifyOTP.parse_args()
        email = args['email']
        entered_otp = args['otp']

        if not email or not entered_otp:
            return {"success" : False, 'message' : 'Invalid requirements'}, 400
        
        verify_otp = EmailVerify.verify_otp(email, entered_otp, datetime.now())
    
        if verify_otp:
            return {"success" : True, 'message': 'Verification successful!'}, 200
        else:
            return {"success" : False, 'message': 'Verification failed. Invalid OTP or expired.'}, 400
        
########## Reset Password ###########
parserResetPassword = reqparse.RequestParser()
parserResetPassword.add_argument('email', type=str, required=True, help='Email is required',  location='json')
parserResetPassword.add_argument('password', type=str, required=True, help='Password is required',  location='json')
parserResetPassword.add_argument('otp', type=str, required=True, help='OTP',  location='json')

@api.route('/resetpassword')  
class ResetPasswordResource(Resource):
    @api.expect(parserResetPassword)
    def post(self):
        args = parserResetPassword.parse_args()
        email = args['email']
        entered_otp = args['otp']
        password = args['password']

        hashed_password = hash_password(password)

        if not email or not entered_otp:
            return {"success" : False, 'message' : 'Invalid requirements'}, 400
        
        verify_otp = EmailVerify.verify_otp(email, entered_otp, datetime.now())
    
        if verify_otp:
            user = User.resetPassword(email, hashed_password)
            User.revokeAllTokens(user["id"])

            return {"success" : True, 'message': 'Password Reset Successful!'}, 200
        else:
            return {"success" : False, 'message': 'Verification failed. Invalid OTP or expired.'}, 400
        
########## Get User Profile ##########

##### User Basic Details #####

@api.route('/user/profile')
class GetUserProfileResource(Resource):
    @jwt_required()
    @login_required
    def get(self,**kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        if not user_id:
            return {"success": False, "message": "Invalid User id"}, 400

        userDetails = User.user_details(user_id)

        if userDetails:
            birthdate = datetime.strptime(str(userDetails['dob']), '%Y-%m-%d').date()
            today = date.today()
            age = relativedelta(today, birthdate).years
            user_info = {
                'user_id': userDetails['id'],
                'email': userDetails['email'],
                'username': userDetails['username'],
                'phone_number': userDetails['phone_number'],
                'dob': str(userDetails['dob']),
                'age': str(age),
                'country' : userDetails['country'],
                'preferred_language' : userDetails['preferred_language'],
                'gender' : userDetails['gender'],
                'gender_others': userDetails['gender_others'],
                'aboutme' : userDetails['aboutme'],
                'created_at' : str(userDetails['created_at']),
                'user_role': userDetails['user_role'],
                'profile_image' : f"{server_domain}static/{app.config['PROFILE_IMAGES_FOLDER']}/{userDetails['profile_image']}"
            }

            languages = UserLanguage.getUserLanguage(user_id)

            categories = UserCategory.get_user_categories(user_id)
            modified_categories = []
            if categories:
                for category in categories:
                    modified_category = {
                        'id': category.get('category_id', None),
                        'name': category.get('name', None),
                        'image': f"{server_domain}static/{app.config['CATEGORY_IMAGES_FOLDER']}/{category.get('image', None)}",
                        'description': category.get('description', None)
                    }
                    modified_categories.append(modified_category)

            locations = UserPref.getAvailableLocations(user_id)
            modified_locations = []
            for i in range(len(locations)):
                modified_locations.append(locations[i][0])
            timeSlots = UserPref.getAvailableTimes(user_id)
            modified_list = []
            for i in range(len(timeSlots)):
                item = {
                    "dayOfWeek": timeSlots.iloc[i]['dayOfWeek'],
                    "timeSlots": timeSlots.iloc[i]['timeSlots']
                }
                modified_list.append(item)
                    
            return {"user_info" : user_info, "languages" : languages, "categories": modified_categories, "locations": modified_locations, "timeSlots": modified_list} , 200

##### User Categories #####
        
@api.route('/user/categories')
class GetUserCategoriesResource(Resource):
    @jwt_required()
    @login_required
    def get(self,**kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        if not user_id:
            return {"success": False, "message": "Invalid User id"}, 400
        
        categories = UserCategory.get_user_categories(user_id)
        modified_categories = []
        if categories:
            for category in categories:
                modified_category = {
                    'id': category.get('category_id', None),
                    'name': category.get('name', None),
                    'image': f"{server_domain}static/{app.config['CATEGORY_IMAGES_FOLDER']}/{category.get('image', None)}",
                    'description': category.get('description', None)
                }
                modified_categories.append(modified_category)
            
            return {"success" : True , "user_category" : modified_categories} , 200

##### User Clubs #####

@api.route('/user/clubs')
class GetUserClubsResource(Resource):
    @jwt_required()
    @login_required
    def get(self,**kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        if not user_id:
            return {"success": False, "message": "Invalid User id"}, 400
        
        clubs = Club.getClubsByMemberID(user_id)

        modified_clubs = []
        if clubs:
            for club in clubs:
                modified_club = {
                    'id': club.get('id', None),
                    'name': club.get('club_name', None),
                    'location': club.get('location', None),
                    'area_code' : club.get('area_code'),
                    'country' : club.get('country', None),
                    'city' : club.get('city', None),
                    'description' : club.get('description', None),
                    'image': f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{club["image"]}'
                }
                modified_clubs.append(modified_club)
            num_clubs = len(modified_clubs)

            return {"success" : True , "user_clubs" : modified_clubs, 'numbers_of_clubs' :num_clubs } , 200
            
##### User Events #####
        
parserGetUserEvents = reqparse.RequestParser()
parserGetUserEvents.add_argument('user_id', type=int, required=True, help='User ID is required')

@api.route('/user/events')
class GetUserEventsResource(Resource):
    @jwt_required()
    @login_required
    def get(self,**kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        if not user_id:
            return {"success": False, "message": "Invalid User id"}, 400
        
        events = Event.get_user_events_by_id(user_id)

        modified_events = []
        if events:
            for event in events:
                modified_event = event.copy()
                modified_event['created_date'] = str(event['created_date'])
                modified_event['meeting_time_start'] = str(event['meeting_time_start'])
                modified_event['meeting_time_end'] = str(event['meeting_time_end'])
                modified_event['cost'] = str(event['cost'])
                modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None

                modified_events.append(modified_event)

            num_events = len(modified_events)
            
            return {"success" : True , "user_events" : modified_events, 'numbers_of_events' :num_events } , 200
         
##### Get all the categories #####
        
@api.route('/category')
class CategoryResource(Resource):
    @api.doc(responses={200: 'Success', 400: 'Validation Error'})
    def get(self):
        category_list = Category.get_all_categories()

        if category_list:
            formatted_categories = []
            for category in category_list:
                formatted_category = {
                    'id': category.get('id', None),
                    'name': category.get('name', None),
                    'image': f'{server_domain}static/{app.config["CATEGORY_IMAGES_FOLDER"]}/{category.get("image", None)}',
                    'description': category.get('description', None)
                }
                formatted_categories.append(formatted_category)

            return formatted_categories,200
        else:
            return {"success": False, "message": "invalid request format"}, 400


##### Add New Category #####

parserAddCategory = reqparse.RequestParser()
parserAddCategory.add_argument('name', type=str, required=True, help='Name', location='json')
parserAddCategory.add_argument('image', type=str, required=True, help='Image', location='json')
parserAddCategory.add_argument('description', type=str, required=True, help='Description',location='json')
parserAddCategory.add_argument('group_ids', type=list, required=True, help='Group IDs', location='json')

@api.route('/category/add')
class AddNewCategoryResource(Resource):
    @api.expect(parserAddCategory)
    def post(self):

        args = parserAddCategory.parse_args()
        name = args['name']
        image = args['image']
        description = args['description']
        group_ids = args['group_ids']

        if not name or not image or not description or not group_ids:
            return {"success": False, "message": "Invalid request format"}, 400
        
        try:
            groups = list(map(int, group_ids))
        except:
            return {"success": False, "message": "Group List must be integers"}, 400
        
        if not isinstance(groups, list):
            return {"success": False, "message": "Invalid group_ids format"}, 400

        if Category.category_exist(name):
            return {"success": False, "message": "Category already exists"}, 400 
        
        groupExist = Group.get_groupbyID(groups) 

        if not groupExist:
            return {"success": False, "message": "Group does not exit"}, 400

        if groupExist :

            try:
                image_data = base64.b64decode(image)         
                filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
                file_path = os.path.join(category_images_folder, filename)

                with open(file_path, 'wb') as file:
                    file.write(image_data)

                category = Category.category(name, filename, description)

                if category:

                    group_ids = [group['id'] for group in groupExist]

                    GroupCategories.groupCategories(category,group_ids)   

                return {"success": True, "message": "categories added"}, 200 
  
            except Exception as e:
                error_message = f"Error decoding or processing image: {str(e)}"
                print(error_message)
                return {"success": False, "message": error_message}, 500


##### Add Categroy for User #####

parserUserAddCategory = reqparse.RequestParser()
parserUserAddCategory.add_argument('category_ids', type=list, required=True, help='Categories', location='json')

@api.route('/user/category/add')
class UserAddCategoryResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUserAddCategory)
    def post(self,**kwargs):

        args = parserUserAddCategory.parse_args()
        current_user = kwargs['current_user']
        user_id = current_user['id']
        category_ids = args['category_ids']
        try:
            categories = list(map(int, category_ids))
            print(categories)
        except:
            return {"success": False, "message": "Category List must be integers"}, 400

        if not user_id or not categories:
            return {"success": False, "message": "Invalid request format"}, 400
        

        if category_ids:
            UserCategory.deleteUserCategory(user_id)
            UserCategory.user_category(user_id,categories);  
            return {"success": True, "message": "Categories added"}, 200
        else:
            return {"success": False, "message": "Invalid Request"}, 400



##### Add Suggest Categroy for User #####

parserUserAddSuggestCategory = reqparse.RequestParser()
parserUserAddSuggestCategory.add_argument('suggested_category', type=str, required=True, help='suggested_category', location='json')

@api.route('/user/category/suggested/add')
class UserAddSuggestCategoryResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUserAddSuggestCategory)
    def post(self,**kwargs):
        
        args = parserUserAddSuggestCategory.parse_args()
        current_user = kwargs['current_user']
        user_id = current_user['id']
        suggested_category = args['suggested_category']

        if not user_id or not suggested_category:
            return {"success": False, "message": "Invalid request format"}, 400
        
        userInfo = UserSuggestCategory.userInfo(user_id);

        if not userInfo:
           return {"success": False, "message": "Username does not exist"}, 400
        
        username = userInfo.get("username")
        
        if Category.category_exist(suggested_category):
            return {"success": False, "message": "Category already exists"}, 400
        
        result = UserSuggestCategory.add_suggest_category(user_id, username, suggested_category)

        if result:
            return {"success": True, "message": "Suggested category added"}, 200
        else:
            return {"success": False, "message": "invalid request format"}, 400
        

##### Get all the suggested categories for Admin #####

@api.route('/category/suggested_category')
class AdminGetSuggestCategoryResource(Resource):
    def get(self):
        suggested_categories_list = UserSuggestCategory.get_all_suggested_categories()

        if not suggested_categories_list:
            return {"success": False, "message": "invalid request format"}, 400
          
        return {"success": True, "message": suggested_categories_list}, 200
    


#####  Get one suggested category by its ID for Admin #####

@api.route('/category/suggested_category/')
@api.doc(params={'id': 'suggestedCategory ID'})
class GetSuggestCategorybyIDResource(Resource):
    def get(self):
        id = request.args.get('id')

        suggested_category = UserSuggestCategory.get_suggested_category(id)

        if not suggested_category:
            return {"success": False, "message": "invalid request format"}, 400
        
        return {"success": True, "message": suggested_category}, 200
    

##### Update suggested category and add New Category by Admin #####

parserUpdateCategory = reqparse.RequestParser()
parserUpdateCategory.add_argument('user_id', type=int, required=True, help='suggestedUser ID', location='json')
parserUpdateCategory.add_argument('name', type=str, required=True, help='Name', location='json')
parserUpdateCategory.add_argument('image', type=str, required=True, help='Image', location='json')
parserUpdateCategory.add_argument('description', type=str, required=True, help='Description', location='json')
parserUpdateCategory.add_argument('group_ids', type=list, required=True, help='Group IDs', location='json')

@api.route('/category/update/')
class UpdateCategoryResource(Resource):
    @api.expect(parserUpdateCategory)
    def post(self):

        args = parserUpdateCategory.parse_args()
        user_id = args['user_id']
        name = args['name'] 
        image = args['image']
        description = args['description']
        group_ids = args['group_ids']

        if not name or not image or not description or not group_ids:
            return {"success": False, "message": "Invalid request format"}, 400
        
        try:
            groups = list(map(int, group_ids))
        except:
            return {"success": False, "message": "Group List must be integers"}, 400
        
        if not isinstance(groups, list):
            return {"success": False, "message": "Invalid group_ids format"}, 400
        
        userExist = UserCategory.user_exists(user_id)

        if not userExist:
            return {"success": False, "message": "User does not exit"}, 400
        
        if Category.category_exist(name):
            return {"success": False, "message": "Category already exists"}, 400

        groupExit = Group.get_groupbyID(groups) 

        if not groupExit:
            return {"success": False, "message": "Group does not exit"}, 400

        if groupExit :      
            try:
                image_data = base64.b64decode(image)
                filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
                file_path = os.path.join(category_images_folder, filename)

                with open(file_path, 'wb') as file:
                    file.write(image_data)

                category = Category.category(name, filename, description)

                if category:

                    adduserSuggestedCategories = UserCategory.user_category(user_id,category)

                    if adduserSuggestedCategories:

                        group_ids = [group['id'] for group in groupExit]

                        result = GroupCategories.groupCategories(category,group_ids)   

                        if result:
                
                            updatedCategories = UserSuggestCategory.update_suggested_categories(user_id) 
                
                            if updatedCategories:
                                return {"success": True, "message": "Categorie updated"}, 200
                            
                            return {"success": False, "message": "Invalid Categorie updated"}, 400
            
            except Exception as e:
                error_message = f"Error decoding or processing image: {str(e)}"
                print(error_message)
                return {"success": False, "message": error_message}, 500


##### Get All the Groups & Categories #####    
            
@api.route('/category_groups')
class GetCategoriesByAllGroupsResource(Resource):
    def get(self):
        groups = Group.get_all_groups()

        if not groups:
            return {"success": False, "message": "invalid request format"}, 400
        
        groupIDs = [group['id'] for group in groups]

        if groupIDs:
            categories = GroupCategories.GetCategoriesByGroups(groupIDs)

        # Assuming categories is a list of integers representing group_ids
        categories_set = set(categories)

        modified_groups = []
        
        for group in groups:
                group_id = group['id']
                modified_group = {
                    'group_id': group_id,  
                    'group_name': group['name'],
                    'group_image': f'{server_domain}static/{app.config["GROUP_IMAGES_FOLDER"]}/{group["image"]}',
                }
                
                # Check if group_id is in the categories_set
                if group_id in categories_set:

                    modified_group['categories'] = [
                        {
                            'category_id': category['category_id'],
                            'category_name': category['category_name'],
                            'description': category['description'],
                            'category_image': f'{server_domain}static/{app.config["CATEGORY_IMAGES_FOLDER"]}/{category["category_image"]}'                             
                        }
                        for category in categories.get(group_id, [])
                    ]
                else:
                    modified_group['categories'] = []

                modified_groups.append(modified_group)

        return {"success": True, "message": modified_groups}, 200

##### Add New Group #####

parserNewGroup = reqparse.RequestParser()
parserNewGroup.add_argument('name', type=str, required=True, help='Name', location='json')
parserNewGroup.add_argument('image', type=str, required=True, help='Image', location='json')

@api.route('/category/group/add')
class NewGroupResource(Resource):
    @api.expect(parserNewGroup)
    def post(self):

        args = parserNewGroup.parse_args()

        name = args['name']
        image = args['image']

        if not name :
            return {"success": False, "message": "Invalid request format"}, 400

        if Group.group_exist(name):
            return {"success": False, "message": "Group already exists"}, 400
        
        try:
            image_data = base64.b64decode(image)         
            filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
            file_path = os.path.join(group_images_folder, filename)

            with open(file_path, 'wb') as file:
                file.write(image_data)

            group = Group.group(name,filename)

            if group:
                return {"success": True, "message": "Group added"}, 200
            else:
                return {"success": False, "message": "Invalid request"}, 400

        except Exception as e:
            error_message = f"Error decoding or processing image: {str(e)}"
            print(error_message)
            return {"success": False, "message": error_message}, 500
        

##### Get All the Groups #####

@api.route('/category/group')
class GetGroupsResource(Resource):
    def get(self):
        groups = Group.get_all_groups()

        if not groups:
            return {"success": False, "message": "invalid request format"}, 400
        
        modified_groups = []

        for group in groups:
            modified_group = {
                "group_id" : group['id'],
                "group_name" : group['name'],
                'group_image': f'{server_domain}static/{app.config["GROUP_IMAGES_FOLDER"]}/{group["image"]}'     
            }

            modified_groups.append(modified_group)
        
        return {"success": True, "message": modified_groups}, 200


##### Get List of events by user_id, registered=True (Events that user is registered for)  ######
###### Get List of events by user_id, registered=False( Events by clubs that user is a member of but haven't registered) #####

parserGetEventByUser = reqparse.RequestParser()
parserGetEventByUser.add_argument('registered', type=str, required=True, help='registered')
parserGetEventByUser.add_argument('pagination', type=int, help='pagination', default= 1)


@api.route('/events/user')
class GetEventByUserResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserGetEventByUser)
    def get(self, **kwargs):
        args = parserGetEventByUser.parse_args()
        current_user = kwargs['current_user']
        user_id = current_user['id']
        registered = args['registered']
        page = args['pagination']


        per_page = 20
        offset = (page-1) * per_page

        if not user_id:
            return {"success": False, "message": "Invalid user_id provided"}, 400
        
        if registered == 'True' or registered is None:
            # User is registered
            events = Event.get_user_events(user_id, per_page, offset)
            if not events:
                return {"success": True, "events": []}, 200
            
            modified_events = []
            for event in events:
                modified_event = event.copy()
                modified_event['created_date'] = str(event['created_date'])
                modified_event['meeting_time_start'] = str(event['meeting_time_start'])
                modified_event['meeting_time_end'] = str(event['meeting_time_end'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
                modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None
                modified_events.append(modified_event)
            
            return {"success": True, "events": modified_events}, 200   
        
        if registered == 'False':
        # User is not registered
            unregistered_events = Event.get_unregister_events(user_id,per_page, offset)

            if unregistered_events is None or len(unregistered_events) == 0:
                return {"success": True, "events": []}, 200
            
            modified_events = []
            for event in unregistered_events:
                modified_event = event.copy()
                modified_event['created_date'] = str(event['created_date'])
                modified_event['meeting_time_start'] = str(event['meeting_time_start'])
                modified_event['meeting_time_end'] = str(event['meeting_time_end'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None

                modified_events.append(modified_event)
            return {"success": True, "events": modified_events}, 200


###### Get List of events by club_id (Events that the club created so far) #####

parserGetEventByClubId = reqparse.RequestParser()
parserGetEventByClubId.add_argument('club_id', type=int, required=True, help='club_id')
parserGetEventByClubId.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/events/club/')
class GetEventByClubIdResource(Resource):
    @api.expect(parserGetEventByClubId)
    def get(self):
        args = parserGetEventByClubId.parse_args()

        club_id = args['club_id']
        page = args['pagination']
        per_page = 20
        offset = (page-1) * per_page

        if not club_id:
            return {"success": False, "message": "club_id is required"}, 400

        events = Event.get_club_events(club_id, per_page, offset)

        if events is None or len(events) == 0:
            return {"success": True, "events": []}, 200

        modified_events = []
        for event in events:
            modified_event = event.copy()
            modified_event['created_date'] = str(event['created_date'])
            modified_event['meeting_time_start'] = str(event['meeting_time_start'])
            modified_event['meeting_time_end'] = str(event['meeting_time_end'])
            modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
            modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None

            modified_events.append(modified_event)
        return {"success": True, "events": modified_events}, 200


###### Get List of events by area_code(Events in the same area code) #####

parserGetEventsNearby = reqparse.RequestParser()
parserGetEventsNearby.add_argument('lat', type=float, required=True, help='lattitude')
parserGetEventsNearby.add_argument('long', type=float, required=True, help='longitude')
parserGetEventsNearby.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/events/')
class GetEventByAreacodeResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserGetEventsNearby)
    def get(self, **kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']
        args = parserGetEventsNearby.parse_args()
        lat = args['lat']
        long = args['long']
        page = args['pagination']
        per_page = 20
        offset = (page-1) * per_page
        
        events = Event.get_nearby_events(user_id, lat, long, 100, per_page,offset)
        
        if events is None or len(events) == 0:
            return {"events": []}, 200

        modified_events = []
        for event in events:
            modified_event = event.copy()
            diff= event['end_date'] - event['start_date']
            days = diff.days
            if(days > 1):
                modified_event['duration'] = f"{diff.days:g} days"
            elif (days > 0):
                modified_event['duration'] = f"{diff.days:g} day"
            elif diff.seconds/3600 > 1:
                modified_event['duration'] = f"{diff.seconds/3600:g} hours"
            else: 
                modified_event['duration'] = f"{diff.seconds/3600:g} hour"
            modified_event['start_date'] = str(event['start_date'])
            modified_event['end_date'] = str(event['end_date'])
            modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
            modified_event['event_image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{event["event_image"]}' if event['event_image'] is not None else None
            modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{event["club_image"]}' if event['club_image'] is not None else None
            modified_events.append(modified_event)
        return {"events": modified_events}, 200

###### Get List of events by area_code(Events in the same area code) #####

parserGetEventByAreacode = reqparse.RequestParser()
parserGetEventByAreacode.add_argument('areacode', type=int, required=True, help='areacode')
parserGetEventByAreacode.add_argument('pagination', type=int, help='pagination', default= 1)
@api.route('/events/area_code/')
class GetEventByAreacodeResource(Resource):
    @api.expect(parserGetEventByAreacode)
    def get(self):
        args = parserGetEventByAreacode.parse_args()

        areacode = args['areacode']
        page = args['pagination']
        per_page = 20
        offset = (page-1) * per_page

        if not areacode:
            return {"success": False, "message": "areacode is required"}, 400
        
        events = Event.get_areacode_events(areacode,per_page,offset)
        
        if events is None or len(events) == 0:
            return {"success": True, "events": []}, 200

        modified_events = []
        for event in events:
            modified_event = event.copy()
            modified_event['created_date'] = str(event['created_date'])
            modified_event['meeting_time_start'] = str(event['meeting_time_start'])
            modified_event['meeting_time_end'] = str(event['meeting_time_end'])
            modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
            modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None

            modified_events.append(modified_event)
        return {"success": True, "events": modified_events}, 200
        
        
######  Get List of events by city (Events in the same city)  #####

parserGetEventByCity = reqparse.RequestParser()
parserGetEventByCity.add_argument('city', type=str, required=True, help='city')
parserGetEventByCity.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/events/city/')
class GetEventByCityResource(Resource):
    @api.expect(parserGetEventByCity)
    def get(self):
        args = parserGetEventByCity.parse_args()

        city = args['city']
        page = args['pagination']
        per_page = 20
        offset = (page-1) * per_page

        if not city:
            return {"success": False, "message": "city name is required"}, 400
        
        events = Event.get_city_events(city,per_page,offset)

        if events is None or len(events) == 0:
            return {"success": True, "events": []}, 200

        modified_events = []
        for event in events:
            modified_event = event.copy()
            modified_event['created_date'] = str(event['created_date'])
            modified_event['meeting_time_start'] = str(event['meeting_time_start'])
            modified_event['meeting_time_end'] = str(event['meeting_time_end'])
            modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
            modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None

            modified_events.append(modified_event)
        return {"success": True, "events": modified_events}, 200


###### Get an event detail #####

parserGetEventDetails= reqparse.RequestParser()
parserGetEventDetails.add_argument('event_id', type=int, required=True, help='event_id')

@api.route('/event/')
class GetEventDetailsResource(Resource):
    @api.expect(parserGetEventDetails)
    def get(self):
        args = parserGetEventDetails.parse_args()

        event_id = args['event_id']

        if not event_id:
            return {"success": False, "message": "Event id is required"}, 400
        
        event = Event.get_event_info(event_id)
        eventAttendees = Event.get_event_attendees(event_id)
        
        if not event:

            return {"success": False, "message": "Invalid event"}, 400
        
        user_info_list = []

        if not eventAttendees:
            user_info_list = []
        
        for eventAttendee in eventAttendees:
            user_info = {
                'user_id': eventAttendee['user_id'],
                'username': eventAttendee['username'],
                'phone_number': eventAttendee['phone_number'],
                'user_role': eventAttendee['user_role']
            }
            user_info_list.append(user_info)

        #adding modified_events
        modified_events = []
        modified_event = event.copy()
        diff= event['end_date'] - event['start_date']
        days = diff.days
        if(days > 1):
            modified_event['duration'] = f"{diff.days:g} days"
        elif (days > 0):
            modified_event['duration'] = f"{diff.days:g} day"
        elif diff.seconds/3600 > 1:
            modified_event['duration'] = f"{diff.seconds/3600:g} hours"
        else: 
            modified_event['duration'] = f"{diff.seconds/3600:g} hour"
        modified_event['created_date'] = str(event['created_date'])
        modified_event['start_date'] = str(event['start_date'])
        modified_event['end_date'] = str(event['end_date'])
        modified_event['event_attendees'] = user_info_list
        modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
        modified_event['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{modified_event["image"]}' if event['image'] is not None else None
        modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{modified_event["club_image"]}' if event['club_image'] is not None else None

        modified_events.append(modified_event)
        
        return {"success": True, "events": modified_events}, 200


###### Post Comment  #####

parserPostComment= reqparse.RequestParser()
parserPostComment.add_argument('post_id', type=int, required=True, help='post_id', location='json')
parserPostComment.add_argument('comment', type=str, required=True, help='comment', location='json')

@api.route('/comment')
class PostCommentResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserPostComment)
    def post(self, **kwargs):
        args = parserPostComment.parse_args()

        post_id = args['post_id']
        current_user = kwargs['current_user']
        user_id = current_user['id']
        comment = args['comment']

        if not post_id or not user_id or not comment:
            return {"success": False, "message": "Invalid request format"}, 400
        
        check_user = User.user_exists_by_id(user_id)

        if not check_user:
            return {"success": False, "message": "User does not exit"}, 400
        
        check_post = CommentPost.check_post(post_id)

        if not check_post:
            return {"success": False, "message": "Post does not exit"}, 400
        
        result = CommentPost.add_comment(post_id,user_id,comment)

        if result:
            return {"success": True, "message": "Comment added"}, 200
        else:
            return {"success": False, "message": "Invalid adding comment"}, 400



######  Get Comments by post id  #####

parserGetComment= reqparse.RequestParser()
parserGetComment.add_argument('post_id', type=int, required=True, help='post_id')
parserGetComment.add_argument('pagination', type=int, help='pagination',  default= 1)
parserGetComment.add_argument('numberofcomments', type=int, help='numberofcomments',  default= 10)


@api.route('/get_comments/')
class GetCommentResource(Resource):
    @api.expect(parserGetComment)
    def get(self):
        args = parserGetComment.parse_args()
        post_id = args['post_id']
        page = args['pagination']
        per_comment = args['numberofcomments']

        offset = (page-1) * per_comment

        if not post_id:
            return {"success": False, "message": "Invalid request format"}, 400
        
        check_post = CommentPost.check_post(post_id)

        if not check_post:
            return {"success": False, "message": "Post does not exit"}, 400
        
        #Get comments
        comments = CommentPost.get_comments_by_post(post_id,per_comment,offset)

        if not comments:
            return {"success": False, "message": "There is no comments"}, 200
        
        modified_comments = []

        for comment in comments:
            modified_comment = {
                'post_id' : comment['post_id'],
                'comment_id': comment['id'],
                'user_id': comment['user_id'],
                'user_name': comment['username'],
                'comment': comment['comment'],
                'date_time': str(comment['date_time'])
            }
            modified_comments.append(modified_comment)

        commentData = {
            'post_id' : post_id,
            'comments' : modified_comments
        }

        return {"success": True, "message" : commentData}, 200


##### Add Club #####

parserAddClub = reqparse.RequestParser()
parserAddClub.add_argument('club_name', type=str, required=True, help='club_name', location='json')
parserAddClub.add_argument('size', type=int, required=True, help='size', location='json')
parserAddClub.add_argument('description', type=str, required=True, help='description', location='json')
parserAddClub.add_argument('country', type=str, required=True, help='country', location='json')
parserAddClub.add_argument('location', type=str, required=True, help='location', location='json')
parserAddClub.add_argument('area_code', type=int, required=True, help='area_code', location='json')
parserAddClub.add_argument('city', type=str, required=True, help='city', location='json')
parserAddClub.add_argument('language_ids', type=list, required=True, help='language_ids',  location='json')
parserAddClub.add_argument('category_ids', type=list, required=True, help='category_ids', location='json')
parserAddClub.add_argument('image', type=str, required=False, help='image', location='json')
parserAddClub.add_argument('is_disabled', type=int, required=True, help='is_disabled', location='json')

@api.route('/club/add')
class AddClubResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserAddClub)
    def post(self,**kwargs):

        args = parserAddClub.parse_args()
        club_name = args['club_name']
        current_user = kwargs['current_user']
        user_id = current_user['id']
        size = args['size']
        description = args['description']
        country = args['country']
        location = args['location']
        area_code = args['area_code']
        city = args['city']
        is_disabled = args['is_disabled']
        language_ids = args['language_ids']
        category_ids = args['category_ids']
        image = args['image']

        try:
            languages = list(map(int, language_ids))
        except:
            return {"success": False, "message": "Language List must be integers"}, 400

        try:
            categories = list(map(int, category_ids))
        except:
            return {"success": False, "message": "Category List must be integers"}, 400
        
        filename = ""
        if image:
            try:
                image_data = base64.b64decode(image)         
                filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
                file_path = os.path.join(clubs_related_folder, filename)

                with open(file_path, 'wb') as file:
                    file.write(image_data)
  
            except Exception as e:
                error_message = f"Error decoding or processing image: {str(e)}"
                print(error_message)
                return {"success": False, "message": error_message}, 500

        club = Club.addClub(club_name, user_id, size, description, location, area_code, country, city, is_disabled, filename)

        if club is None:
            return {"success": False, "message": "Failed to add club"}, 400

        addedLanguages = []
        addedLanguages = ClubLanguage.addClubLanguage(club['id'], language_ids)
        
        addedCategories = []
        addedCategories = ClubCategory.addClubCategory(club['id'], categories)

    
        member = ClubMember.addClubMember(club['id'], user_id)

        modified_member = []
        modified_member = member.copy()
        modified_member['date_time'] = str(member['date_time'])


        return {"message": "Club added successfully", "club": club,
                             "club_languages": addedLanguages, "club_categories": addedCategories,
                             "club_member": modified_member}, 200


##### Update Club #####

parserUpdateClub = reqparse.RequestParser()
parserUpdateClub.add_argument('id', type=int, required=True, help='id')
parserUpdateClub.add_argument('club_name', required=True, type=str, help='club_name', location='json')
parserUpdateClub.add_argument('size', required=True, type=int, help='size', location='json')
parserUpdateClub.add_argument('description', required=True, type=str, help='description', location='json')
parserUpdateClub.add_argument('country', required=True, type=str, help='country', location='json')
parserUpdateClub.add_argument('location', required=True, type=str, help='location', location='json')
parserUpdateClub.add_argument('area_code', required=True, type=int, help='area_code', location='json')
parserUpdateClub.add_argument('city', required=True, type=str, help='city', location='json')
parserUpdateClub.add_argument('language_ids', type=list, required=True, help='language_ids', location='json')
parserUpdateClub.add_argument('category_ids', type=list, required=True, help='category_ids', location='json')
parserUpdateClub.add_argument('image', type=str, required=False, help='image', location='json')

@api.route('/club/update')
class UpdateClubResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUpdateClub)
    def put(self, *args, **kwargs):

        args = parserUpdateClub.parse_args()
        club_id = args['id']
        club_name = args['club_name']
        size = args['size']
        description = args['description']
        country = args['country']
        location = args['location']
        area_code = args['area_code']
        city = args['city']
        language_ids = args['language_ids']
        category_ids = args['category_ids']
        image = args['image']

        try:
            languages = list(map(int, language_ids))
        except:
            return {"success": False, "message": "Language List must be integers"}, 400

        try:
            categories = list(map(int, category_ids))
        except:
            return {"success": False, "message": "Category List must be integers"}, 400
        
        filename = ""
        if image:
            try:
                image_data = base64.b64decode(image)         
                filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
                file_path = os.path.join(clubs_related_folder, filename)

                with open(file_path, 'wb') as file:
                    file.write(image_data)
  
            except Exception as e:
                error_message = f"Error decoding or processing image: {str(e)}"
                print(error_message)
                return {"success": False, "message": error_message}, 500

        current_user = kwargs['current_user']

        if club_id:
            isOrganizer = Club.getClubAndUserID(club_id, current_user['id'])
            if isOrganizer:
                updated_club = Club.updateClub(club_name, size, description, location, area_code, country, city, filename, club_id)


                if updated_club is None:
                    return {"success": False, "message": "Failed to update club"}, 400

                addedLanguages = []

                if language_ids:
                    ClubLanguage.deleteClubLanguage(club_id)

                addedLanguages = ClubLanguage.addClubLanguage(updated_club['id'], language_ids)

                addedCategories = []

                if category_ids:
                    ClubCategory.deleteClubCategory(club_id)

                addedCategories = ClubCategory.addClubCategory(updated_club['id'], category_ids)

                return {"message": "Club updated successfully", "club": updated_club,
                                        "club_languages": addedLanguages, "club_categories": addedCategories,
                                        }, 200
            else:
                return {"message": "Not found"}, 404

##### Get Club List #####

parserGetClub = reqparse.RequestParser()
parserGetClub.add_argument('member', type=str, help='member')
parserGetClub.add_argument('organizer', type=str, help='organizer')             
parserGetClub.add_argument('area_code', type=int, help='area_code')             
parserGetClub.add_argument('city', type=str, help='city')   
parserGetClub.add_argument('suggested_for', type=str, help='suggested_for')             

@api.route('/clubs')
class GetClubsResource(Resource):
    @api.expect(parserGetClub)
    def get(self):
        args = parserGetClub.parse_args()
        member = args['member']
        organizer = args['organizer']
        area_code = args['area_code']
        city = args['city']
        suggested_for = args['suggested_for']

        if member:
            clubs = Club.getClubsByMemberID(member)
        elif organizer:
            clubs = Club.getClubsByOrganizerID(organizer)
        elif area_code:
            clubs = Club.getClubsByAreaCode(area_code)
        elif city:
            clubs = Club.getClubsByCity(city)
        elif suggested_for:
            clubs = Club.getClubsSuggested(suggested_for)
        
        if clubs.length > 0:
            for club in clubs: 
                modified_club = club.copy()
                modified_club['image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{club["image"]}'
                club = modified_club
            return {"clubs": clubs}
        else:
            return {"message": "Not found"}, 404
            

##### Get Club Details by Club ID #####

parserGetClubById = reqparse.RequestParser()
parserGetClubById.add_argument('id', type=int, help='ClubID')

@api.route('/club')
class GetClubByIdResource(Resource):
    @api.expect(parserGetClubById)
    def get(self):
        args = parserGetClubById.parse_args()
        id = args['id']
        club = Club.getClubsById(id)  # Define `club` here
        modified_club = club.copy()
        modified_club['image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{club["image"]}'
        if club:
            clubMembers = ClubMember.getClubMembersByClubId(id)
            return {"club": modified_club, "club_members": clubMembers}
        else:
            return {"message": "Invalid request"}



##### Join Club  #####

parserJoinClub = reqparse.RequestParser()
parserJoinClub.add_argument('club_id', type=int, required=True, help='club_id', location='json')

@api.route('/club/join')
class JoinClubResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserJoinClub)
    def post(self, **kwargs):

        args = parserJoinClub.parse_args()

        current_user = kwargs['current_user']
        user_id = current_user['id']
        club_id = args['club_id']

        isJoined = ClubMember.club_member_exists(club_id, user_id)

        if not isJoined:
            ClubMember.addClubMember(club_id, user_id, role_id = 2)

            return {"message": "Joining club successful"}, 200
        else: 
            return {"message": "There is an error joining this club"}, 400
    
  ##### User Leave Club #####

parserUserLeaveClub = reqparse.RequestParser()
parserUserLeaveClub.add_argument('club_id', type=int, required=True, help='club_id', location='json')
parserUserLeaveClub.add_argument('requested_by', type=int, required=True, help='requested_by', location='json')
parserUserLeaveClub.add_argument('reason', type=str, required=True, help='reason', location='json')

@api.route('/user/leave/club')
class UserLeaveClubResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUserLeaveClub)
    def post(self,**kwargs):
        args = parserUserLeaveClub.parse_args()

        current_user = kwargs['current_user']
        user_id = current_user['id']
        club_id = args['club_id']
        requested_by = args['requested_by']
        reason = args['reason']

        if not user_id or not club_id or not requested_by or not reason:
            return {"success": False, "message": "Invalid request format"}, 400
        
        check_user = UserLeaveClub.check_user(club_id,user_id)

        if not check_user:
            return {"success": False, "message": "There is no user with the same club id"}, 400
        
        deletedUser = UserLeaveClub.delete_user(club_id,user_id)

        if deletedUser:
            leave_club = UserLeaveClub.add_user_leave_club(user_id,club_id,requested_by,reason)

            if not leave_club:
                return {"success": False, "message": "Invalid adding user leave club"}, 400

            return {"success": True, "message": leave_club}, 200   
        

##### Disable Clubs  #####
        
parserDisableClub = reqparse.RequestParser()
parserDisableClub.add_argument('id', type=int, required=True, help='club_id', location='json')
      
@api.route('/club/disable')
class DisableClubResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserDisableClub)
    def put(self, *args, **kwargs):

        args = parserDisableClub.parse_args()

        club_id = args['id']
        current_user = kwargs['current_user']
        user_id = current_user['id']

        if not club_id or not user_id:
            return {"success": False, "message": "Invalid requirements"}, 400
        
        club = Club.getClubsById(club_id)

        Organizer_id = club['user_id']

        if not user_id == Organizer_id:
            return {"Success" : False , "Message" : "You don't have permission to disable the club"}
        
        disableClub = Club.disableClub(club_id)

        if disableClub:
            return {"Success" : True , "Message" : "Disable Club Successful"}
        else:
            return {"Success" : False , "Message" : "Invalid Club Disable"}
        
##### Create Events  #####

parserCreateEvent = reqparse.RequestParser()

parserCreateEvent.add_argument('club_id', type=int, required=True, help='club_id', location='json')
parserCreateEvent.add_argument('event_name', type=str, required=True, help='event_name', location='json')
parserCreateEvent.add_argument('start_time', type=str, required=True, help='meeting_time_start', location='json')
parserCreateEvent.add_argument('end_time', type=str, required=True, help='meeting_time_end', location='json')
parserCreateEvent.add_argument('start_date', type=str, required=True, help='start_date', location='json')
parserCreateEvent.add_argument('end_date', type=str, required=True, help='end_date', location='json')
parserCreateEvent.add_argument('description', type=str, required=True, help='description of the event', location='json')
parserCreateEvent.add_argument('address', type=str, required=True, help='address first line', location='json')
parserCreateEvent.add_argument('building_name', type=str, help='building name(if any)', location='json')
parserCreateEvent.add_argument('area_code', type=int, required=True, help='area_code', location='json')
parserCreateEvent.add_argument('city', type=str, required=True, help='city', location='json')
parserCreateEvent.add_argument('state', type=str, help='state(if any)', location='json')
parserCreateEvent.add_argument('country', type=str, required=True, help='country', location='json')
parserCreateEvent.add_argument('is_private', type=int, required=True, help='is_private', location='json')
parserCreateEvent.add_argument('max_size', type=int, required=True, help='max_size', location='json')
parserCreateEvent.add_argument('cost', type=float, required=True, help='cost', location='json')
parserCreateEvent.add_argument('currency', type=str, required=True, help='currency', location='json')
parserCreateEvent.add_argument('image', type=str, required=False, help='image', location='json')
@api.route('/event/add')
class CreateEventResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserCreateEvent)
    def post(self,**kwargs):
        args = parserCreateEvent.parse_args()

        club_id = args['club_id']
        event_name = args['event_name']
        time_start_str = args['start_time']
        time_end_str = args['end_time']
        start_date_str = args['start_date']
        end_date_str = args['end_date']

        start_datetime_str = start_date_str + " " + time_start_str
        end_datetime_str = end_date_str + " " + time_end_str


        # Parse time strings into time objects
        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M').isoformat() if start_datetime_str is not None else None
        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M').isoformat() if end_datetime_str is not None else None

        description = args['description']
        
        address = args['address']
        building_name = args['building_name']
        area_code = args['area_code']
        city = args['city']
        state = args['state']
        country = args['country']
        is_private = args['is_private']
        
        current_user = kwargs['current_user']
        user_id = current_user['id']

        max_size = args['max_size']
        cost = args['cost']
        currency = args['currency']
        image = args['image']

        if(not Country.checkCurrency(currency)):
            return {"message": "Invalid Currency"}, 400

        filename = ""
        if image:
            try:
                image_data = base64.b64decode(image)         
                filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'
                file_path = os.path.join(events_related_folder, filename)

                with open(file_path, 'wb') as file:
                    file.write(image_data)
  
            except Exception as e:
                error_message = f"Error decoding or processing image: {str(e)}"
                print(error_message)
                return {"success": False, "message": error_message}, 500


        isOrganizer = ClubMember.club_member_exists(club_id, user_id)

        if isOrganizer is not None and isOrganizer['role_id'] == app.config['CONFIG_ORGANIZER_ROLE']:

            clubEvent = ClubEvent.addClubEvent(
                club_id, user_id, event_name, description,
                start_datetime, end_datetime,
                address, building_name, area_code, city, state, country, is_private, max_size, cost, currency, 
                filename 
            )

            EventAttendee.addEventAttendee(clubEvent['id'], user_id, 'ORGANIZER')

            if clubEvent:
                clubEvent_json = clubEvent.copy()
                clubEvent_json['created_date'] = str(clubEvent_json['created_date'])
                clubEvent_json['start_date'] = str(clubEvent_json['start_date'])
                clubEvent_json['end_date'] = str(clubEvent_json['end_date'])
                clubEvent_json['cost'] = int(clubEvent_json['cost'])
                clubEvent_json['image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{clubEvent_json["image"]}' if clubEvent_json['image'] is not None else None

                return {"message": "Event created successfully", "clubEvent": clubEvent_json}, 201
            else:
                return {"message": "Event creation failed"}, 400
        else:
            return {"message": "You are not the organizer"}, 401

##### Event Payment #####

parserPayment = reqparse.RequestParser()
parserPayment.add_argument('event_id', type=int, required=True, help='Event ID', location='json')
parserPayment.add_argument('number_of_tickets', type=int, required=True, help='number of tickets', location='json')
parserPayment.add_argument('payment_amount', type=int, required=True, help='Payment Amount', location='json')
parserPayment.add_argument('payment_type', type=str, required=True, help='Payment Type', location='json')
parserPayment.add_argument('address', type=str, required=True, help='User Address', location='json')
parserPayment.add_argument('postal_code', type=str, required=True, help='Postal Code', location='json')
parserPayment.add_argument('town', type=str, required=True, help='User Town', location='json')
parserPayment.add_argument('country', type=str, required=True, help='User Country', location='json')

@api.route('/event/payment')  
class PaymentResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserPayment)
    def post(self,**kwargs):
        args = parserPayment.parse_args()
        current_user = kwargs['current_user']
        user_id = current_user['id']
        event_id = args['event_id']
        number_of_tickets = args['number_of_tickets']
        payment_type = args['payment_type']
        payment_amount = args['payment_amount']
        address = args['address']
        postal_code = args['postal_code']
        town = args['town']
        country = args['country']
        client_ip = request.remote_addr

        if not event_id or not number_of_tickets or not payment_type or not client_ip or not address or not postal_code or not town or not country:
            return {"Success" : False, "Message" : "Invalid Request"}, 400
        
        event_info = Event.get_event_info(event_id)

        if not event_info:
            return {"success" : False, "message" : "No Events Found"}, 400

        event_cost = Event.get_event_cost(event_id).get('cost') 

        if not event_cost:
            event_cost = 0
        
        amount_total = event_cost * number_of_tickets
        system_fee = 5
        seat_fee = number_of_tickets
        all_total = amount_total + system_fee + seat_fee
        nett_amount = ( all_total / 125 ) * 100
        # nett_amount = all_total * 0.8
        tax = all_total - nett_amount

        invoice_number = Payment.get_next_invoice_number()

        alreadyBought = Payment.has_user_already_bought(user_id, event_id)

        if alreadyBought:
            return {"Success" : False, "Message" : "Already Bought!"}, 200

        tickets = []
        for _ in range(number_of_tickets):
            # Generate a ticket number
            new_ticket_number = generate_ticket_number()

            # Check if the ticket number already exists
            existing_ticket = Payment.get_next_ticket_number(new_ticket_number)

            if existing_ticket:
                # If ticket number already exists, generate a new one
                while existing_ticket:
                    new_ticket_number = generate_ticket_number()
                    existing_ticket = Payment.get_next_ticket_number(new_ticket_number)

            tickets.append(new_ticket_number)

            qr_data = f"Ticket Number: {new_ticket_number}, User ID: {user_id}, Event ID: {event_id}"
            qr_image_path = os.path.join(qr_images_folder, f"ticket_{new_ticket_number}.png")
            generate_qr_code(qr_data, qr_image_path)

        if tickets:
            
            NewInvoice = Payment.addPayment(invoice_number, number_of_tickets, payment_type, payment_amount, user_id, event_id, client_ip, address, postal_code, town, country, event_cost, amount_total, all_total, nett_amount, tax)

            if NewInvoice:

                addTicket = Payment.addTicket(invoice_number, tickets)

                if addTicket:

                    print("this is event : ", event_info)

                    modified_event = event_info.copy()
                    modified_event['created_date'] = str(event_info['created_date'])
                    modified_event['meeting_time_start'] = str(event_info['meeting_time_start'])
                    modified_event['meeting_time_end'] = str(event_info['meeting_time_end'])
                    modified_event['cost'] = str(event_info['cost'])

                    return {"success": True,"invoice_number": invoice_number, "payment_type": payment_type, "tickets": tickets, "event" : modified_event}, 200
        
        return {"Success": False, "Message": "Error while processing payment"}, 400


##### Add New Post   #####

parserAddNewPost = reqparse.RequestParser()

parserAddNewPost.add_argument('club_id', type=int, required=True, help='club_id', location='json')     
parserAddNewPost.add_argument('organizer_id', type=int, help='organizer_id', location='json')     
parserAddNewPost.add_argument('post_subject', type=str, required=True, help='post_subject', location='json')  
parserAddNewPost.add_argument('image_links', type=list, required=True, help='image_links', location='json')

@api.route('/post/add')
class NewPostResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserAddNewPost)
    def post(self, *args, **kwargs):
        args = parserAddNewPost.parse_args()

        club_id = args['club_id']
        current_user = kwargs['current_user']
        organizer_id = current_user['id']
        post_subject = args['post_subject']
        image_links = args['image_links']

        isClub = Club.getClubsById(club_id)

        isJoined = ClubMember.club_member_exists(club_id, organizer_id)

        if not isJoined:
            return {"message": "You are not the member of this club"}, 400

        if isClub:
            post = Post.addPost(organizer_id, club_id, post_subject)

            if image_links is not None:
                images = []

                for image in image_links:
                    # Decode base64-encoded image data
                    image_data = base64.b64decode(image)

                    # Generate a unique filename using the SHA-256 hash of the image data
                    filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'

    
                    file_path = os.path.join(post_images_folder, filename)

                    print(filename)

                    images.append(filename)

                    # Save the image data to the file
                    with open(file_path, 'wb') as file:
                        file.write(image_data)

            PostImage.addPostImage(post['id'], images)
            
            return {"success": True, "message": "post added"}, 200
        else:
            return {"success": False, "message": "Club doesn't exist"}, 400
        
##### DELETE Post   #####
parserDeletePost = reqparse.RequestParser()

parserDeletePost.add_argument('id', type=int, required=True, help='id') 
parserDeletePost.add_argument('club_id', type=int, required=True, help='club_id')     
parserDeletePost.add_argument('organizer_id', type=int, help='organizer_id')    

@api.route('/post/delete')
class NewPostResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserDeletePost)
    def delete(self, *args, **kwargs):
        args = parserDeletePost.parse_args()

        post_id = args['id']
        club_id = args['club_id']
        current_user = kwargs['current_user']
        organizer_id = current_user['id']

        isPost = Post.getPost(post_id)

        if not isPost:
            return {"success": False, "message": "Post doesn't exist"}, 400

        isJoined = ClubMember.club_member_exists(club_id, organizer_id)

        if isJoined is not None and (isJoined['role_id'] == app.config['CONFIG_ORGANIZER_ROLE'] or isJoined['role_id'] == 2):
            Post.delete_post(post_id)
            return {"message": "Post deleted"}, 202
        else:
            return {"message": "You are not the member of this club"}, 400

            

##### React Post   #####

parserReactPost = reqparse.RequestParser()

parserReactPost.add_argument('post_id', type=int, required=True, help='post_id', location='json')     
parserReactPost.add_argument('react_id', type=int, required=True, help='react_id', location='json')      

@api.route('/post/react')
class ReactPostResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserReactPost)
    def post(self,**kwargs):
        args = parserReactPost.parse_args()

        post_id = args['post_id']
        react_id = args['react_id']
        current_user = kwargs['current_user']
        user_id = current_user['id']

        postReact = PostReact.addReact(post_id, user_id, react_id)

        if postReact:
            postReactData = postReact.copy()

            postReactData['date_time'] = str(postReactData['date_time'])

            return {"success": True, "post": postReactData}, 200
        else:
            return {"message": "There is an error reacting to this post"}, 404
        

##### Get all the languages #####
        
@api.route('/language')
class GetLanguageResource(Resource):
    def get(self):
        language_list = Language.get_all_languages()
        if language_list:
            formatted_languages = []
            for language in language_list:
                formatted_language = {
                    'language_id': language.get('id', None),
                    'language_name': language.get('name', None)
                }
                formatted_languages.append(formatted_language)

            return {"success": True, "languages": formatted_languages}, 200
        else:
            return {"success": False, "message": "invalid request format"}, 400


# api.add_resource(ReactPostResource, '/post/react')

        
# Get all posts by club_id

parserGetPost = reqparse.RequestParser()
parserGetPost.add_argument('club_id', type=int, required=True, help='club_id')  

@api.route('/get_posts/')
class GetPostResource(Resource):
    @api.expect(parserGetPost)
    def get(self):
        args = parserGetPost.parse_args()

        club_id = args['club_id']
        page = request.args.get('pagination', default=1, type=int)
        per_page = 20
        offset = (page-1) * per_page

        posts = Post.getPosts(club_id,per_page,offset)

        if not posts:
            return {"success" : True, "Posts" : "No posts available"}, 200
        
        modified_posts = []
        for post in posts:
            post_id = post['id']
            modified_post = post.copy()
            modified_post['last_updated'] = str(post['last_updated'])

            post_images = PostImage.getPostImages(post_id)
            modified_post['postImage'] = [f"{server_domain}static/{app.config['POST_IMAGES_FOLDER']}/{post_image.get('image_link', None)}" for post_image in post_images]

            total_reacts = PostReact.getReact(post_id)
            totalReacts = total_reacts[0].get('total_reacts', 0) if total_reacts else 0

            react_types = PostReact.getReactTypes(post_id)

            modified_post['reacts'] = {
                'total_reacts': totalReacts,
                'react_types': react_types
            }

            per_comment = 5
            comments = CommentPost.get_comments_by_post(post_id,per_comment,offset)

            modified_comments = []
            if comments:
                for comment in comments:
                    modified_comment = {
                        'comment_id': comment['id'],
                        'user_id': comment['user_id'],
                        'user_name': comment['username'],
                        'comment': comment['comment'],
                        'date_time': str(comment['date_time'])
                    }

                    modified_comments.append(modified_comment)
            
            modified_post['comments'] = modified_comments

            modified_posts.append(modified_post)

        return {"success": True, "Posts": modified_posts}, 200
      


## GET REACT BY POST ID

parserGetReactPost = reqparse.RequestParser()
parserGetReactPost.add_argument('post_id', type=int, required=True, help='post_id')
parserGetReactPost.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/get_reacts')
class GetReactPostResource(Resource):
    @api.expect(parserGetReactPost)
    def get(self):
        args = parserGetReactPost.parse_args()

        post_id = args['post_id']
        page = args['pagination']

        per_page = 20
        offset = (page-1) * per_page

        post = Post.getPost(post_id)

        if not post:
            return {"success": False, "message": "Post not found"}, 400
        
        reacts = PostReact.getPostReactByID(post_id, per_page, offset)

        if reacts is not None and len(reacts) > 0:
            reactsCopy = []
            for react in reacts:
                reactCopy = react.copy()
                reactCopy['react_time'] = str(reactCopy['react_time'])
                reactsCopy.append(reactCopy)

            return {"post_id": post_id, "reacts": reactsCopy}, 200
        else:
            return {"success": False, "message": "Not found"}, 404
        
##### Add Local News #####

parserLocalNews = reqparse.RequestParser()
parserLocalNews.add_argument('title_en', type=str, required=True, help='Title in English', location='json')
parserLocalNews.add_argument('overview_en', type=str, required=True, help='Overview in English', location='json')
parserLocalNews.add_argument('subject_en', type=str, required=True, help='Subject in English', location='json')
parserLocalNews.add_argument('category_en', type=str, required=True, help='Category in English', location='json')
parserLocalNews.add_argument('main_pic', type=str, required=True, help='Main Picture', location='json')
parserLocalNews.add_argument('title_fo', type=str, required=True, help='Title in Farsi', location='json')
parserLocalNews.add_argument('overview_fo', type=str, required=True, help='Overview in Faroese', location='json')
parserLocalNews.add_argument('subject_fo', type=str, required=True, help='Subject in Faroese', location='json')
parserLocalNews.add_argument('category_fo', type=str, required=True, help='Category in Faroese', location='json')
parserLocalNews.add_argument('pic_1', type=str, help='Picture 1 Base64', location='json')
parserLocalNews.add_argument('pic_2', type=str, help='Picture 2 Base64', location='json')
parserLocalNews.add_argument('pic_3', type=str, help='Picture 3 Base64', location='json')
parserLocalNews.add_argument('pic_4', type=str, help='Picture 4 Base64', location='json')
parserLocalNews.add_argument('source', type=str, required=True, help='Source of the news', location='json')
parserLocalNews.add_argument('news_link', type=str, required=True, help='News Link URL', location='json')
parserLocalNews.add_argument('original_date', type=str, required=True, help='orignal date', location='json')
parserLocalNews.add_argument('video_link', type=str, help='Video Link URL', location='json')

@api.route('/news/add')
class AddLocalNewsRequest(Resource):
    @api.expect(parserLocalNews, validate=True)
    @jwt_required()
    @role_required([1]) 
    def post(self, *args, **kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']
        args = parserLocalNews.parse_args()

        required_fields = [
            'title_en', 'overview_en', 'subject_en', 'category_en',
            'main_pic', 'title_fo', 'overview_fo', 'subject_fo', 'category_fo',
            'source', 'news_link', 'original_date'
        ]

        for field in required_fields:
            if not args[field]:
                return {"success": False, "message": "Invalid Request Format"}, 400
            
        images = {}
        image_filenames = {}

        for img in ['main_pic', 'pic_1', 'pic_2', 'pic_3', 'pic_4']:
            image_data = args[img]
            if image_data:
                image_decoded = base64.b64decode(image_data)
                image_filename = f'{hashlib.sha256(image_decoded).hexdigest()}.jpg'
                image_path = os.path.join(news_related_folder, image_filename)
                
                with open(image_path, 'wb') as file:
                    file.write(image_decoded)
                images[img] = image_decoded
                image_filenames[img] = image_filename
            else:
                image_filenames[img] = None
        try:
            result = LocalNews.addNews(
                user_id, args['title_en'], args['overview_en'], args['subject_en'],
                args['category_en'], args['title_fo'], args['overview_fo'], args['subject_fo'],
                args['category_fo'], image_filenames['main_pic'], image_filenames['pic_1'],
                image_filenames['pic_2'], image_filenames['pic_3'], image_filenames['pic_4'],
                args['source'], args['news_link'], args['original_date'],args.get('video_link', None)
            )

            if result:
                return {"success": True, "message": "Local News added"}, 200 
        except Exception as e:
            error_message = f"Error decoding or processing image: {str(e)}"
            print(error_message)
            return {"success": False, "message": error_message}, 500

##### Set User Event Preferences #####

parserSetUserPref = reqparse.RequestParser()
parserSetUserPref.add_argument('availableTimes', type=list, required=True, help='Available times for each day of the week', location='json', )
parserSetUserPref.add_argument('location', type=list, required=True, help='List of preferred locations', location='json')

set_user_pref_model = api.model('RequestBody', {
    'availableTimes': fields.List(fields.Nested(api.model('timeSlots',{
        'dayOfWeek': fields.String(required=True, description='The day of the week', example='Monday'),
        'timeSlots': fields.List(fields.String, required=True, description='The available timeslots for the day', example=['2:00pm-5:00pm', '5:00pm-8:00pm'])
    })), required=True, description='Available times for each day of the week', example=[{
        'dayOfWeek': 'Monday',
        'timeSlots': ["2:00pm-5:00pm", "5:00pm-8:00pm"]
    }, {
        'dayOfWeek': 'Friday',
        'timeSlots': ["2:00pm-5:00pm", "5:00pm-8:00pm"]
    }]),
    'location': fields.List(fields.String, required=True, description='List of preferred locations', example=['Torshavn', 'Hoyvoik'])
})


@api.route('/set_preferences')
class SetUserPrefRequest(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserSetUserPref,set_user_pref_model)
    def post(self, **kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        # Parse the request body
        args = parserSetUserPref.parse_args()
        available_times = args['availableTimes']
        location = args['location']

        if not user_id:
            return {"success": False, "message": "Invalid User id"}, 400

        if len(available_times) > 7:
            return {'success': False, 'message': 'Invalid number of available times'}, 400
        
        deleteTimes = UserPref.deleteAvailableTimes(user_id)
        deleteLocations = UserPref.deleteAvailableLocations(user_id)

        addedTimes = UserPref.addAvailableTimes(user_id, available_times)
        addedLocations = UserPref.addAvailableLocations(user_id, location)

        if addedTimes and addedLocations:
            return {'success': True ,'message': 'User Event Preferences processed successfully'}, 200
        
        return {'success': False ,'message': "Failed"}, 400


## GET REACT BY POST ID

parserGetReactPost = reqparse.RequestParser()
parserGetReactPost.add_argument('post_id', type=int, required=True, help='post_id')
parserGetReactPost.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/get_reacts')
class GetReactPostResource(Resource):
    @api.expect(parserGetReactPost)
    def get(self):
        args = parserGetReactPost.parse_args()

        post_id = args['post_id']
        page = args['pagination']

        per_page = 20
        offset = (page-1) * per_page

        post = Post.getPost(post_id)

        if not post:
            return {"success": False, "message": "Post not found"}, 400
        
        reacts = PostReact.getPostReactByID(post_id, per_page, offset)

        if reacts is not None and len(reacts) > 0:
            reactsCopy = []
            for react in reacts:
                reactCopy = react.copy()
                reactCopy['react_time'] = str(reactCopy['react_time'])
                reactsCopy.append(reactCopy)

            return {"post_id": post_id, "reacts": reactsCopy}, 200
        else:
            return {"success": False, "message": "Not found"}, 404
        
##### Countries  #####
        
addcountry_model = api.model('RequestBody_AddCountry', {
    'countries': fields.List(fields.Nested(api.model('CountryInfo', {
        'name': fields.String(required=True, description='The name of the country', example='Afghanistan'),
        'countrycode': fields.String(required=True, description='The country code', example='AF'),
        'phcode': fields.String(required=True, description='The country phone code', example='+93'),
    })), required=True, description='List of countries with their codes')
})

parserAddCountry = reqparse.RequestParser()
parserAddCountry.add_argument('countries', type=list, required=True, help='countries name', location='json')


@api.route('/add/countries')
class PostCountryResource(Resource):
    @api.expect(parserAddCountry, addcountry_model)
    def post(self):
        args = parserAddCountry.parse_args()

        countries = args['countries']

        if not countries:
            return {"success" : False, "message" : "Invalid name and countrycode and phcode"}, 400
        
        result = Country.addCountryInfo(countries)

        if result:
            return {"success" : True, "message" : " Countries info successfully added"}, 200
        else:
            return {"success" : False, "message" : " Error while adding countries information "}, 400



##### Get all the countries #####
        
@api.route('/countries')
class CountryResource(Resource):
    def get(self):
        country_list = Country.getCountries()

        if country_list:
            formatted_countries = []
            for country in country_list:
                formatted_country = {
                    'id': country.get('id', None),
                    'name': country.get('country', None),
                    'code': country.get('countrycode', None),
                    'phcode': '+' + str(country.get('phcode', None))
                }
                formatted_countries.append(formatted_country)

            return formatted_countries, 200
        else:
            return {"success": False, "message": "invalid request format"}, 400



##### Friend Connect #####

parserUserConnect = reqparse.RequestParser()
parserUserConnect.add_argument('user_id', type=int, required=True, help='user_id', location='json')
      
@api.route('/user/connect')
class UserConnectResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUserConnect)
    def post(self, *args, **kwargs):

        args = parserUserConnect.parse_args()

        user_id = args['user_id']
        current_user = kwargs['current_user']

        if not user_id or not current_user:
            return {"success": False, "message": "Invalid requirements"}, 400
        
        isAlreadyFriend = UserConnect.isAlreadyFriend(user_id,current_user['id'])

        if isAlreadyFriend:
            return {"success" : False, "message" : "Already Friend"}, 400
        
        result = UserConnect.user_connect(current_user['id'],user_id)

        if result:
            return {'success' : True, "message" : "Friend request sends successfully"}, 200
        else:
            return{'success' : False, "message" : "Failed to send friend request"}

##### Get Friend Requests #####
      
@api.route('/user/requests')
class UserRequestResource(Resource):
    @jwt_required()
    @login_required
    def get(self, **kwargs):
        try:

            current_user = kwargs['current_user']

            if not current_user:
                return {"success": False, "message": "Invalid requirements"}, 400
            
            result = UserConnect.user_requests(current_user['id'])

            print("this is result : ", result)
            if result:
                modified_users = []
            
                for user in result:
                        modified_user = {
                            'requested_user_id': user['requested_user_id'],  
                            'username': user['username'],
                            'requested_time' : str(user['requested_time']),
                            'profile_image': f'{server_domain}static/{app.config["PROFILE_IMAGES_FOLDER"]}/{user["profile_image"]}',
                            'accept' : user['accept']
                        }

                        modified_users.append(modified_user)

                return {'success' : True, "message" : modified_users}, 200
            else:
                return{'success' : True, "message" : "There is no friend request"}, 200   
        except Exception as e:
            print(f"Error in UserRequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400
        
##### Friend Request Accept #####

parserUserAccept = reqparse.RequestParser()
parserUserAccept.add_argument('user_id', type=int, required=True, help='user_id', location='json')
parserUserAccept.add_argument('accept', type=int, choices=[0, 1], required=True, help='accept', location='json')

@api.route('/user/accept')
class UserAcceptResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserUserAccept)
    def post(self, *args, **kwargs):

        args = parserUserAccept.parse_args()

        user_id = args['user_id']
        current_user = kwargs['current_user']
        accept = args['accept']

        if user_id is None or current_user is None or accept is None:
                return {"success": False, "message": "Invalid requirements"}, 400
        
        if accept == 1:

            result = UserConnect.user_accept(current_user['id'],user_id)

            if result:
                return {'success': True, "message": "Friend request accepted successfully"}, 200
            else:
                return {'success': False, "message": "Friend request acceptance failed"}, 400

        else:

            result = UserConnect.user_cancel(current_user['id'],user_id)

            if result:
                return {'success': True, "message": "Friend request cancelled"}, 200
            else:
                return {'success': False, "message": "Friend request cancellation failed"}, 400
            
##### Get User Friends #####
      
@api.route('/user/friends')
class UserFriendResource(Resource):
    @jwt_required()
    @login_required
    def get(self, **kwargs):
        try:
            current_user = kwargs['current_user']

            if not current_user:
                return {"success": False, "message": "Invalid requirements"}, 400
            
            result = UserConnect.user_friends(current_user['id'])

            if result:

                modified_users = []
            
                for user in result:
                        modified_user = {
                            'user_id': user['id'],  
                            'username': user['username'],
                            'profile_image': f'{server_domain}static/{app.config["PROFILE_IMAGES_FOLDER"]}/{user["profile_image"]}',
                        }

                        modified_users.append(modified_user)

                return {'success' : True, "message" : modified_users}, 200
            else:
                return{'success' : True, "message" : "There is no friend"}, 200   
        except Exception as e:
            print(f"Error in UserRequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400

parserAddUserPost = reqparse.RequestParser()

parserAddUserPost.add_argument('location', type=str, required=True, help='location')     
parserAddUserPost.add_argument('subject', type=str, required=True, help='subject')  
parserAddUserPost.add_argument('is_public', type=int, required=True, help='is_public') 
parserAddUserPost.add_argument('photos', required=True, help='photos', action="append")


@api.route('/user/post')
class UserPostResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserAddUserPost)
    def post(self, **kwargs):
        args = parserAddUserPost.parse_args()
        current_user = kwargs['current_user']
        user_id = current_user['id']
        location = args['location']
        subject = args['subject']
        is_public = args['is_public']
        photos = args['photos']

        post = UserPost.addUserPost(user_id, subject, location, is_public)

        if post:
            if photos is not None:
                images = []

                for image in photos:
                    # Decode base64-encoded image data
                    image_data = base64.b64decode(image)

                    # Generate a unique filename using the SHA-256 hash of the image data
                    filename = f'{hashlib.sha256(image_data).hexdigest()}.jpg'

    
                    file_path = os.path.join(user_post_images_folder, filename)

                    print(filename)

                    images.append(filename)

                    # Save the image data to the file
                    with open(file_path, 'wb') as file:
                        file.write(image_data)

                PostImage.addUserPostImage(post['id'], images)

            return {"success": True, "message": "post added"}, 200

        else:
            return {"success": False, "message": "Error adding post"}, 400 

## GET POST BY USER ID

parserGetUserPost = reqparse.RequestParser()

@api.route('/user/posts')
class GetUserPostResource(Resource):
    @login_required
    @api.expect(parserGetUserPost)
    def get(self, **kwargs):
        current_user = kwargs['current_user']
        user_id = current_user['id']

        post = UserPost.getUserPost(user_id)

        if post:
            return {"post": post}, 200
        else:
            return {"success": False, "message": "Not found"}, 404

parserGetUserFriendPost = reqparse.RequestParser()
parserGetUserFriendPost.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/user/friends/post')
class GetUserFriendPostResource(Resource):
    @login_required
    @api.expect(parserGetUserFriendPost)
    def get(self, **kwargs):
        args = parserGetUserFriendPost.parse_args()

        current_user = kwargs['current_user']
        user_id = current_user['id']
        page = args['pagination']
        per_page = 20
        offset = (page-1) * per_page

        post = UserPost.getUserFriendPost(user_id, per_page, offset)

        if post:
            for friend_post in post:
                friend_post['created_time'] = str(friend_post['created_time'])
            return {"post": post}, 200
        else:
            return {"success": False, "message": "Not found"}, 404
    
@api.route('/timezone')
class TimezoneResource(Resource):
    def get(self, **kwargs):
        try: 
            timezones = []
            result = Timezone.get()
            for timezone in result:
                timezones.append(timezone['timezone'])

            if result:
                return {"timezones" : timezones }, 200
            else:
                return{"message" : "Something went wrong!"}, 500   
        except Exception as e:
            print(f"Error in UserRequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400

parserGetLocalNews = reqparse.RequestParser()
parserGetLocalNews.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/news')
class GetNewsResource(Resource):
    @api.expect(parserGetLocalNews)
    def get(self):
        args = parserGetLocalNews.parse_args()

        page = args['pagination']

        per_page = 20
        offset = (page-1) * per_page

        result = LocalNews.get_news(per_page, offset)

        if result:
            for news_item in result:
                news_item['created_time'] = str(news_item['created_time'])
                for pic_name in ['main_pic', 'pic_1', 'pic_2', 'pic_3', 'pic_4']:
                    if news_item[pic_name] is not None and news_item[pic_name] != "":
                        news_item[pic_name] = f'{server_domain}static/{app.config["NEWS_RELATED_FOLDER"]}/{news_item[pic_name]}'
            return {"success": True, "news": result}, 200
        else:
            return {"success": False, "message": "No posts"}, 400


#####  Get nearby cities for lat and long #####

parserLocation = reqparse.RequestParser()
parserLocation.add_argument('lat', type=str, required=True, help='latitude', location='json')
parserLocation.add_argument('long', type=str, required=True, help='longitude', location='json')
parserLocation.add_argument('distance', type=int, required=True, help='distance(km)', location='json')

@api.route('/nearby_cities')
class NearbyCityResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserLocation)
    def post(self, *args, **kwargs):
        try: 
            args = parserLocation.parse_args()
            lat = float(args['lat'])
            long = float(args['long'])
            distance = args['distance']

            result = GeoCity.getNearbyCities(long, lat, distance)
            if result:
                return {"cities" : result }, 200
            else:
                return{"message" : "Something went wrong!"}, 500   
        except Exception as e:
            print(f"Error in UserRequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400
        
#####  Get suggested users #####
@api.route('/suggested_users')
class SuggestedUserResource(Resource):
    @jwt_required()
    @login_required
    def get(self, **kwargs):
        try: 
            current_user = kwargs['current_user']
            result = UserSuggest.getSuggestedUsers(current_user['id'])
            users = []
            for user in result: 
                modified_user = user.copy()
                modified_user['dob'] = str(user['dob'])
                birthdate = datetime.strptime(modified_user['dob'], '%Y-%m-%d').date()
                today = date.today()
                age = relativedelta(today, birthdate).years
                
                modified_user['age'] = age
                modified_user['profile_image'] = f"{server_domain}static/{app.config['PROFILE_IMAGES_FOLDER']}/{modified_user['profile_image']}"
                users.append(modified_user)
            if result:
                return {"users" : users }, 200
            else:
                return{"message" : "Something went wrong!"}, 500   
        except Exception as e:
            print(f"Error in SuggestedUserResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400
        
#####Get suggested events####
parserGetEventsSuggested = reqparse.RequestParser()
parserGetEventsSuggested.add_argument('pagination', type=int, help='pagination', default= 1)
@api.route('/suggested_events')
class SuggestedUserResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserGetEventsSuggested)
    def get(self, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserGetEventsSuggested.parse_args()
            page = args['pagination']
            per_page = 20
            offset = (page-1) * per_page
            events = UserSuggest.getSuggestedEvents(user_id, per_page, offset)
            if events is None or len(events) == 0:
                return {"events": []}, 200

            modified_events = []
            for event in events:
                modified_event = event.copy()
                diff= event['end_date'] - event['start_date']
                days = diff.days
                if(days > 1):
                    modified_event['duration'] = f"{diff.days:g} days"
                elif (days > 0):
                    modified_event['duration'] = f"{diff.days:g} day"
                elif diff.seconds/3600 > 1:
                    modified_event['duration'] = f"{diff.seconds/3600:g} hours"
                else: 
                    modified_event['duration'] = f"{diff.seconds/3600:g} hour"
                modified_event['start_date'] = str(event['start_date'])
                modified_event['end_date'] = str(event['end_date'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
                modified_event['event_image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{event["event_image"]}' if event['event_image'] is not None else None
                modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{event["club_image"]}' if event['club_image'] is not None else None
                modified_events.append(modified_event)
            return {"events": modified_events}, 200
        except Exception as e:
            print(f"Error in SuggestedUserResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400

## Events Save for later
parserSaveEvent = reqparse.RequestParser()
parserSaveEvent.add_argument('event_id', type=int, required=True, help='event ID')
@api.route('/save_for_later')
class SaveEvents(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserSaveEvent)
    def post(self, *args, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserSaveEvent.parse_args()
            event_id = args['event_id']

            result = Event.saveForLater(event_id, user_id)
            if result:
                return {"success": True, "message": "Event is saved."}, 200
            else:
                return{"message" : "Something went wrong!"}, 500   
        except Exception as e:
            print(f"Error in RequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400


##### Saved events ####
parserGetSavedEvents = reqparse.RequestParser()
parserGetSavedEvents.add_argument('pagination', type=int, help='pagination', default= 1)
@api.route('/saved_events')
class GetSavedEvents(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserGetSavedEvents)
    def get(self, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserGetSavedEvents.parse_args()
            page = args['pagination']
            per_page = 20
            offset = (page-1) * per_page
            events = Event.getSavedEvents(user_id, per_page, offset)
            if events is None or len(events) == 0:
                return {"events": []}, 200

            modified_events = []
            for event in events:
                modified_event = event.copy()
                diff= event['end_date'] - event['start_date']
                days = diff.days
                if(days > 1):
                    modified_event['duration'] = f"{diff.days:g} days"
                elif (days > 0):
                    modified_event['duration'] = f"{diff.days:g} day"
                elif diff.seconds/3600 > 1:
                    modified_event['duration'] = f"{diff.seconds/3600:g} hours"
                else: 
                    modified_event['duration'] = f"{diff.seconds/3600:g} hour"
                modified_event['start_date'] = str(event['start_date'])
                modified_event['end_date'] = str(event['end_date'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
                modified_event['event_image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{event["event_image"]}' if event['event_image'] is not None else None
                modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{event["club_image"]}' if event['club_image'] is not None else None
                modified_events.append(modified_event)
            return {"events": modified_events}, 200
        except Exception as e:
            print(f"Error in SuggestedUserResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400

##### Joined events ####
parserJoinedEvents = reqparse.RequestParser()
parserJoinedEvents.add_argument('pagination', type=int, help='pagination', default= 1)
@api.route('/joined_events')
class GetJoinedEvents(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserJoinedEvents)
    def get(self, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserJoinedEvents.parse_args()
            page = args['pagination']
            per_page = 20
            offset = (page-1) * per_page
            events = Event.getJoinedEvents(user_id, per_page, offset)
            if events is None or len(events) == 0:
                return {"events": []}, 200

            modified_events = []
            for event in events:
                modified_event = event.copy()
                diff= event['end_date'] - event['start_date']
                days = diff.days
                if(days > 1):
                    modified_event['duration'] = f"{diff.days:g} days"
                elif (days > 0):
                    modified_event['duration'] = f"{diff.days:g} day"
                elif diff.seconds/3600 > 1:
                    modified_event['duration'] = f"{diff.seconds/3600:g} hours"
                else: 
                    modified_event['duration'] = f"{diff.seconds/3600:g} hour"
                modified_event['start_date'] = str(event['start_date'])
                modified_event['end_date'] = str(event['end_date'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
                modified_event['event_image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{event["event_image"]}' if event['event_image'] is not None else None
                modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{event["club_image"]}' if event['club_image'] is not None else None
                modified_events.append(modified_event)
            return {"events": modified_events}, 200
        except Exception as e:
            print(f"Error in SuggestedUserResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400
        
##### Joined events ####
parserOrganizedEvents = reqparse.RequestParser()
parserOrganizedEvents.add_argument('pagination', type=int, help='pagination', default= 1)
@api.route('/organized_events')
class GetJoinedEvents(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserOrganizedEvents)
    def get(self, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserOrganizedEvents.parse_args()
            page = args['pagination']
            per_page = 20
            offset = (page-1) * per_page
            events = Event.getOrganizedEvents(user_id, per_page, offset)
            if events is None or len(events) == 0:
                return {"events": []}, 200

            modified_events = []
            for event in events:
                modified_event = event.copy()
                diff= event['end_date'] - event['start_date']
                days = diff.days
                if(days > 1):
                    modified_event['duration'] = f"{diff.days:g} days"
                elif (days > 0):
                    modified_event['duration'] = f"{diff.days:g} day"
                elif diff.seconds/3600 > 1:
                    modified_event['duration'] = f"{diff.seconds/3600:g} hours"
                else: 
                    modified_event['duration'] = f"{diff.seconds/3600:g} hour"
                modified_event['start_date'] = str(event['start_date'])
                modified_event['end_date'] = str(event['end_date'])
                modified_event['cost'] = str(event['cost']) if event['cost'] is not None else None
                modified_event['event_image'] =  f'{server_domain}static/{app.config["EVENT_IMAGES_FOLDER"]}/{event["event_image"]}' if event['event_image'] is not None else None
                modified_event['club_image'] =  f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{event["club_image"]}' if event['club_image'] is not None else None
                modified_events.append(modified_event)
            return {"events": modified_events}, 200
        except Exception as e:
            print(f"Error in SuggestedUserResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400

#####  Joined Clubs  #####

parserJoinedClubs = reqparse.RequestParser()
parserJoinedClubs.add_argument('pagination', type=int, help='pagination', default= 1)

@api.route('/joined_club')
class JoinedClubsResource(Resource):
    @jwt_required()
    @login_required
    @api.expect(parserJoinedClubs)
    def get(self, *args, **kwargs):
        try: 
            current_user = kwargs['current_user']
            user_id = current_user['id']
            args = parserJoinedClubs.parse_args()
            page = args['pagination']
            per_page = 20
            offset = (page-1) * per_page

            joinedClubs = Club.getJoinedClubs(user_id,per_page,offset)

            modified_clubs = []
            for club in joinedClubs:

                modified_club = {
                    'club_id': club['id'],
                    'club_name': club['club_name'],
                    'user_id': club['user_id'],
                    'size': club['size'],
                    'description': club['description'],
                    'location': club['location'],
                    'area_code': club['area_code'],
                    'country': club['country'],
                    'city': club['city'],
                    'image': f'{server_domain}static/{app.config["CLUB_IMAGES_FOLDER"]}/{club["image"]}' if club.get('image') else None, 
                    'is_disabled': club['is_disabled'],
                }

                modified_clubs.append(modified_club)

            return{"success" : True , "message": modified_clubs}, 200   

        except Exception as e:
            print(f"Error in UserRequestResource: {e}")
            return {"success": False, "message": "An error occurred while processing your request"}, 400
if __name__ == '__main__':
    if app.config['IS_DEV']:
        app.run(debug=True)
    else:
        app.run(debug=False)
