from flask import Flask, request,render_template
from flask_restful import Resource,Api,reqparse
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256 as sha256
import os
import datetime
from flask_mail import Mail, Message
from random import choice
from string import ascii_uppercase
import json



app=Flask(__name__)
api = Api(app)


parser= reqparse.RequestParser(bundle_errors=True)
parser.add_argument('first_name', help="first name field can not be blank", required=True)
parser.add_argument('last_name', help="last name field can not be blank", required=True)
parser.add_argument('father_name', help="father name field can not be blank", required=True)
parser.add_argument('DOB', help="DOB field can not be blank", required=True)
parser.add_argument('gender', help="Gender field can not be blank", required=True)
parser.add_argument('highest_qualification', help="Highest Qualification field can not be blank", required=True)
parser.add_argument('martial_status', help="Marital Status field can not be blank", required=True)
parser.add_argument('contact_details', help="Contact details field can not be blank", required=True)
parser.add_argument('email_address', help="Email Address field is can not be blank", required=True)
parser.add_argument('password', help="Password field can not be blank", required=True)
parser.add_argument('confirm_password', help="Email Address field is can not be blank", required=True)
parser.add_argument('exp_journalism', help="Exp. in Journalism field is can not be blank", required=True)
parser.add_argument('adhar_no', help="Adhar no field is can not be blank", required=True)
parser.add_argument('pan_no', help="Pan no field is can not be blank", required=True)
parser.add_argument('present_address', help="Present Address Details field is can not be blank", required=True)


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Admin@123'
app.config['MYSQL_DB']='LNIDB'


app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME= 'an.pradeepp@gmail.com',
    MAIL_PASSWORD='pradeep@817'
)
mail=Mail(app)
mysql=MySQL(app)

country=[]

@app.route('/')
def mani():
    return render_template('login.html')


class Add_Reporter(Resource):
    def post(self):
        data=parser.parse_args()
        cur = mysql.connection.cursor()
        email=data['email_address']

        cur.execute("""SELECT email_address FROM Reporter_Details WHERE email_address = '%s' """ %(email))
        res=cur.fetchone()

        if res is not None:
            return {'message':'Requested user {} already exits'.format(res)}


        first_name=data['first_name']
        last_name=data['last_name']
        father_name=data['father_name']
        dob=data['DOB']
        gender=data['gender']
        highest_qualification=data['highest_qualification']
        martial_status=data['martial_status']

        contact_details=data['contact_details']
        contact_details=contact_details.replace('\'','\"')

        email_address=data['email_address']
        password=data['password']
        confirm_password=data['confirm_password']
        exp_journalism=data['exp_journalism']
        adhar_no=data['adhar_no']
        pan_no=data['pan_no']
        present_address=data['present_address']
        present_address=present_address.replace('\'','\"')

        permanent_address=data['permanent_address']
        permanent_address=permanent_address.replace('\'','\"')

        address_where_lni=data['address_where_lni']
        address_where_lni=address_where_lni.replace('\'','\"')


        if password == confirm_password:
            password=sha256.hash(password)

            cur.execute("INSERT INTO Reporter_Details(first_name,last_name,father_name,email_address,password,dob,gender,highest_qualification,marital_status,contact_details,exp_in_jurnalism,adhar_no,pan_no,present_address,status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)",(first_name,last_name,father_name,email_address,password,dob,gender,highest_qualification
            ,martial_status,contact_details,exp_journalism,adhar_no,pan_no,present_address,"deactive"))
            mysql.connection.commit()
            cur.close()
            otp=generate_otp()
            send_otp(email_address,first_name,otp)
            return {'message':"Success"},201
        else:
            return {'message':"Confirm Password do not match Password"}

def sendMail(email_address,username,otp):
    try:
        msg = Message("OTP- LOCAL NEWS OF INDIA",
           sender="an.pradeepp@gmail.com",
           recipients=[email_address])
        print(email_address)
        msg.body= 'Hello '+username+',\nYOUR OTP IS '+ otp + '\nWe have sent a otp please verify your otp with app'
        mail.send(msg)
        return 'Mail sent'

    except Exception as e:
        print(str(e))
        return str(e)



def send_otp(email_address,username,otp):

    cur=mysql.connection.cursor()
    suffix= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO otp_verfity(otp,reporter_email,start_date) VALUES(%s,%s,%s)", (otp,email_address,suffix))
    mysql.connection.commit()
    cur.close()
    sendMail(email_address,username,otp)
    return "otp sent"




class Resend_OTP(Resource):
    def post(self):
        parser= reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email_address', help="Email field can not be blank", required=True)
        cur=mysql.connection.cursor()
        data=parser.parse_args()

        email=data['email_address']

        cur.execute("""SELECT * FROM otp_verfity WHERE reporter_email = '%s' """ %(email))
        res=cur.fetchone()

        if res is None:
            return {'message':'email is not valid {}'.format(email)}


        cur.execute("""SELECT * FROM Reporter_Details WHERE email_address = '%s' """ %(email))
        username=cur.fetchone()

        print(username[2])

        suffix= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        otp=''.join(choice(ascii_uppercase) for i in range(6))
        cur.execute("UPDATE otp_verfity SET otp= '%s', start_date= '%s' WHERE reporter_email= '%s' "%(otp,suffix,email))
        mysql.connection.commit()
        cur.close()
        sendMail(email,username[2],otp)
        return {'message':'otp sent please check your email'}

def generate_otp():
    otp=''.join(choice(ascii_uppercase) for i in range(6))

    return otp


class User_Login(Resource):
    def post(self):
        parser= reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email_address', help="Email field can not be blank", required=True)
        parser.add_argument('password', help="password field can not be blank", required=True)
        data=parser.parse_args()

        cur=mysql.connection.cursor()
        email=data['email_address']
        password=data['password']
        cur=mysql.connection.cursor()
        cur.execute("""SELECT * FROM Reporter_Details WHERE email_address = '%s'"""%(email))
        user=cur.fetchone()

        if not user:
            return {'message':"Requested User {} not exists".format(email)},400


        if sha256.verify(password,user[6]):
            userDetails={
                "First name":user[2],
                "Last name":user[3],
                "Father name":user[4],
                "Email":user[5],
                "DOB":str(user[7]),
                "Gender":user[8],
                "Highest Qualification":user[9],
                "Marital Status":user[10],
                "Contact Details":json.JSONDecoder().decode(user[11]),
                "Experiance in Journalisam":user[12],
                "Adhar no":user[13],
                "Pan no":user[14],
                "Present details":json.JSONDecoder().decode(user[15]),
                "Permanent details":json.JSONDecoder().decode(user[16]),
                "Address Where LNI Proposed":json.JSONDecoder().decode(user[17]),
                "Image":user[18],
                "status":user[19]
            }
            return {'message':"Success",'userDetails':userDetails}, 200, {'Content-Type':'application/json'}
            # return json.dumps(user_details)
        else:
            return {'message':"password is wrong"},400


class Country(Resource):
    def get(self):

        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM countries")
        countries=cur.fetchall()

        country_data=[]

        for country in countries:

            country_details={
                "countryID":country[0],
                "short Name":country[1],
                "Country name":country[2],
                "Phone code":country[3]
            }
            country_data.append(country_details)
        return {'message':"success",'countries':country_data},200,{'Content-Type':'application/json'}

class States(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument("country_id", help="Country is can not blank",required=True)
        data=pdata=parser.parse_args()

        country_id=data["country_id"]

        cur=mysql.connection.cursor()
        cur.execute("""SELECT * FROM states WHERE country_id = '%s' """ %(country_id))
        states=cur.fetchall()

        state_data=[]

        for state in states:
            states_details={
                "stateId":state[0],
                "State name":state[1]
            }
            state_data.append(states_details)
        return {'message':"success","states_details":state_data}, 200, {'Content-Type':'application/json'}

class Cities(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument("state_id", help="State id field can not blank", required=True)
        data=parser.parse_args()

        state_id=data["state_id"]

        cur=mysql.connection.cursor()
        cur.execute(""" SELECT * FROM cities WHERE state_id = '%s' """%(state_id))
        cities=cur.fetchall()

        citie_data=[]

        for citie in cities:
            cities_details={
                "city id":citie[0],
                "city name":citie[1]
            }
            citie_data.append(cities_details)
        return {"message":"success","cities_details":citie_data},200, {'Content-Type':'application/json'}

class Update_user(Resource):
    def post(self):
        parser= reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email_address', help="Email Address field is can not be blank", required=True)
        parser.add_argument('image', help="Image field can not be blank", required=True)
        parser.add_argument('socila_media', help="Social media field can not be blank", required=True)
        parser.add_argument('language_speak', help="Language speak field can not be blank", required=True)
        parser.add_argument('language_write', help="Language write field can not be blank", required=True)
        parser.add_argument('Driving_l_no', help="Driving licence no field can not be blank", required=True)
        parser.add_argument('passport_no', help="Passport no field can not be blank", required=True)
        parser.add_argument('present_income_source', help="Present income source field can not be blank", required=True)
        parser.add_argument('family_income_source', help="Family income source field can not be blank", required=True)
        parser.add_argument('banking_details', help="banking details field can not be blank", required=True)
        parser.add_argument('permanent_address', help="Permanent Address Details field is can not be blank", required=True)
        parser.add_argument('address_where_lni', help="Address Where LNI Praposed field is can not be blank", required=True)

        data=parser.parse_args()

        email=data['email_address']
        cur=mysql.connection.cursor()

        cur.execute("""SELECT email_address FROM Reporter_Details WHERE email_address = '%s' """ %(email))
        res=cur.fetchone()

        if res is None:
            return {'message':'Requested user {} does not exits'.format(email)}



        dl_no=data['Driving_l_no']
        passport_no=data['passport_no']

        socila_media=data['socila_media']
        socila_media=socila_media.replace('\'','"')

        present_income_source=data['present_income_source']
        present_income_source=present_income_source.replace('\'','"')
        family_income_source=data['family_income_source']
        family_income_source=family_income_source.replace('\'','"')

        language_speak=data['language_speak']
        language_speak=language_speak.replace('\'','"')

        language_write=data['language_write']
        language_write=language_write.replace('\'','"')

        banking_details=data['banking_details']
        banking_details=banking_details.replace('\'','"')

        permanent_address=data['permanent_address']
        permanent_address=permanent_address.replace('\'','"')

        address_lni_proposed=data['address_where_lni']
        address_lni_proposed=address_lni_proposed.replace('\'','"')

        address_lni_proposed=data['address_where_lni']
        address_lni_proposed=address_lni_proposed.replace('\'','"')



        cur.execute("UPDATE Reporter_Details SET image='%s',socialmedia_details='%s', language_speak='%s',language_write='%s',dl_no='%s',passport_no='%s',present_income_source='%s',family_income_source='%s',permanent_address='%s',address_where_lni='%s',banking_details='%s' WHERE email_address='%s'" %("",socila_media,language_speak,language_write,dl_no,passport_no,present_income_source,family_income_source,
            permanent_address,address_lni_proposed,banking_details,email))
        mysql.connection.commit()
        cur.close()

        return {"message":"User updated successfully"}


if __name__=='__main__':

    api.add_resource(Add_Reporter, '/add_user')
    api.add_resource(Resend_OTP, '/resend_otp')
    api.add_resource(User_Login, '/user_login')
    api.add_resource(Country, '/countries')
    api.add_resource(States, '/states')
    api.add_resource(Cities, '/cities')
    api.add_resource(Update_user, '/update_reporter')
    app.run(debug=True)
    
