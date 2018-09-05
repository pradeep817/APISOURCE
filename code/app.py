from flask import Flask, request,jsonify
from flask_restful import Resource, Api,reqparse
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256 as sha256
import os
import datetime
import json



app = Flask(__name__)
api = Api(app)

APP_ROOT=os.path.dirname(os.path.abspath(__file__))

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='electline_db'
mysql=MySQL(app)

output=[]


parser = reqparse.RequestParser(bundle_errors=True)

parser.add_argument('first_name', help="First Name field can not be blank", required=True)
parser.add_argument('last_name', help="Last Name field can not be blank", required=True)
parser.add_argument('father_name', help="Father Name field can not be blank", required=True)
parser.add_argument('DOB', help="DOB field can not be blank", required=True)
parser.add_argument('email', help="Email field can not be blank", required=True)
parser.add_argument('gender', help="Gender field can not be blank", required=True)
parser.add_argument('password', help="Password field can not be blank", required=True)
parser.add_argument('confirm_password', help="Confirm Password field can not be blank",required=True)

parser.add_argument('mobile_no', help="Phone field can not be blank", required=False)



class Add_user(Resource):

    def post(self):
        data=parser.parse_args()

        cur=mysql.connection.cursor()
        email=data["email"]
        cur.execute("""SELECT email_address FROM UserDetails WHERE email_address = '%s' """%(email))
        userdata=cur.fetchall()

        for user in userdata:
            if userdata[1] is not None:
                return {'message': "Requested User '{}' already exists".format(user)},400


        # target = os.path.join(APP_ROOT,'/images')
        #
        # if not os.path.isdir(target):
        #     os.mkdir(target)
        #
        # for file in request.files.getlist("file"):
        #     suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        #     filename=file.filename
        #     imagename=suffix+filename
        #     destination="_".join([target,imagename])
        #     print(destination)

        first_name=data['first_name']
        last_name=data['last_name']
        father_name=data['father_name']
        dob=data['DOB']
        gender=data['gender']


        # print(marital_status)

        if data['password'] == data['confirm_password']:
            password=sha256.hash(data['password'])
            cur.execute("INSERT INTO UserDetails(first_name,last_name,father_name,DOB,gender,email_address,password) VALUES(%s, %s, %s, %s, %s, %s, %s)",(first_name,last_name,father_name,dob,gender,email,password))
            mysql.connection.commit()
            cur.close()

            return {'message':"Success"},201
        else:
            return {'message':"Confirm Password do not match Password"}


class User_login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', help="Email field can not be blank", required=True)
        parser.add_argument('password', help="Password field can not be blank", required=True)

        data=parser.parse_args()

        email=data['email']
        password=data['password']
        cur=mysql.connection.cursor()
        cur.execute("""SELECT * FROM UserDetails WHERE email_address = '%s'"""%(email))
        user=cur.fetchone()

        if not user:
            return {'message':"Requested User {} not exists".format(data['email'])},400


        if sha256.verify(password,user[7]):
            result=user[11]

            loaded_json = json.loads(result)
            for x in loaded_json:

                data = {}
                data[x] = loaded_json[x]
                json_data = json.dumps(data)
                output.append(json_data)
            print(output)

            print(result)
            dictionaryToJson = json.dumps(result)
            print(dictionaryToJson)
            user_details={
                "First Name":user[1],
                "Last Name":user[2],
                "DOB":str(user[3]),
                "Gender":str(user[4]),
                "Phone":str(user[5]),
                "Email Address":user[6],
                "Contact Details" :json.JSONDecoder().decode(result)

            }
            return {'message':"Success",'userDetails':user_details}, 200, {'Content-Type':'application/json'}
            # return json.dumps(user_details)
        else:
            return {'message':"password is wrong"},400


class Update_User(Resource):
    def put(self):

        parser=reqparse.RequestParser()
        parser.add_argument('email', help="Email field can not be blank", required=True)
        parser.add_argument('highest_qualification', help="Highest Qualification field can not be blank", required=True)
        parser.add_argument('martial_status', help="Martial Status field can not be blank")
        parser.add_argument('contact_details', location='json', help="Contact field can not be blank", required=True)

        parser.add_argument('social_media_details', help="Socia Media Details field can not be blank")
        parser.add_argument('experience_journalism', help="Experience Journalism field can not be blank", required=True)
        parser.add_argument('language_speak', help="Language Speak field can not be blank", required=True)
        parser.add_argument('language_write', help="Language Write field can not be blank", required=True)
        parser.add_argument('adhar_no', help="Adhar No field can not be blank", required=True)
        parser.add_argument('pan_no', help="Pan No field can not be blank", required=True)
        parser.add_argument('dl_no', help="DL No field can not be blank")

        parser.add_argument('passport_no', help="Passport No Password field can not be blank")
        parser.add_argument('present_income_source', help="Present Income Source field can not be blank")
        parser.add_argument('family_income_source', help="Family Income Source field can not be blank")
        parser.add_argument('present_address', help="Present Address field can not be blank", required=True)
        parser.add_argument('permanent_address', help="Permanent Address field can not be blank", required=True)
        parser.add_argument('address_lni_proposed', help="Address Lni Proposed field can not be blank", required=True)
        parser.add_argument('banking_details', help="Banking Details field can not be blank", required=True)


        data=parser.parse_args()
        cur=mysql.connection.cursor()
        email=data['email']
        cur.execute(""" SELECT email_address FROM UserDetails WHERE email_address= '%s' """%(email))
        users=cur.fetchone()

        if users is None:
            return {'message':'User does not register'},400


        highest_qualification = data['highest_qualification']
        marital_status=data['martial_status']
        socialmedia_details=data['social_media_details']
        experience_journalism=data['experience_journalism']

        adhar_no=data['adhar_no']
        pan_no=data['pan_no']
        dl_no=data['dl_no']
        passport_no=data['passport_no']


        present_income_source=data['present_income_source']
        present_income_source=present_income_source.replace('\'','"')
        family_income_source=data['family_income_source']
        family_income_source=family_income_source.replace('\'','"')


        contact_details=data['contact_details']
        print("con"+contact_details)
        contact_details=contact_details.replace('\'','\"')
        print("con"+contact_details)
        language_speak=data['language_speak']
        language_speak=language_speak.replace('\'','"')

        language_write=data['language_write']
        language_write=language_write.replace('\'','"')

        present_address=data['present_address']
        present_address=present_address.replace('\'','"')
        permanent_address=data['permanent_address']
        permanent_address=permanent_address.replace('\'','"')
        address_lni_proposed=data['address_lni_proposed']
        address_lni_proposed=address_lni_proposed.replace('\'','"')

        banking_details=data['banking_details']
        banking_details=banking_details.replace('\'','"')

        cur.execute("UPDATE UserDetails SET image='%s',marital_status='%s',highest_qualification='%s',contact_details='%s',experience_journalism='%s',language_speak='%s',language_write='%s',adhar_no='%s',pan_no='%s',dl_no='%s',passport_no='%s',present_income_source='%s',family_income_source='%s',present_address='%s',permanent_address='%s',address_lni_proposed='%s',banking_details='%s',socialmedia_details='%s' WHERE email_address='%s'" %("",marital_status,highest_qualification,contact_details,experience_journalism,language_speak,language_write,adhar_no,pan_no,dl_no,passport_no,present_income_source,family_income_source,present_address,permanent_address,address_lni_proposed,banking_details,socialmedia_details,email))
        mysql.connection.commit()
        cur.close()

        return {'message':"Success"},201





if __name__=='__main__':
    api.add_resource(Add_user, '/register')
    api.add_resource(User_login, '/login')
    api.add_resource(Update_User, '/update')
    app.run(debug=True)
    app.run(port=5000)
