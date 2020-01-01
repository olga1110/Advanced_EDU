#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class CharField:
    def __init__(self, required, nullable, name='', default=None):
        self.name = "_" + name
        self.type = str
        self.required = required
        self.nullable = nullable
        self.default = default

    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)

    def __set__(self, instance, value):
        if self.required:
            if value is None:
                # raise ValueError(f'attribute {self.name[1:]} is required')
                logging.error(f'Validation Error: attribute {self.name[1:]} is required;')
            if not self.nullable and not value:
                # raise ValueError(f"attribute {self.name[1:]} can't be null")
                logging.error(f"Validation Error: attribute {self.name[1:]} can't be null;")
        if value and not isinstance(value, self.type):
            # raise TypeError('Must be a str')
            logging.error(f"Validation Error: attribute {self.name[1:]} must be a str;")
        setattr(instance, self.name, value)
    # def __delete__(self, instance):
    #     raise AttributeError("Can't delete attribute")


class DateField(object):
    def __init__(self, required, nullable, name='', date_format='%d.%m.%Y', default=None):
        self.name = "_" + name
        self.type = str
        self.required = required
        self.nullable = nullable
        self.date_format = date_format
        self.default = default

    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)
        # __getattribute__

    def __set__(self, instance, value):
        if self.required:
            if value is None:
                logging.error(f'Validation Error: attribute {self.name[1:]} is required;')
                # raise ValueError(f'attribute {self.name[1:]} is required')
            if not self.nullable and not value:
                # raise ValueError(f"attribute {self.name[1:]} can't be null")
                logging.error(f"Validation Error: attribute {self.name[1:]} can't be null;")
        if value and not isinstance(value, self.type):
            # raise TypeError('Input date in str format')
            logging.error(f'Validation Error: attribute {self.name[1:]} must be input in str format;')
        try:
            if value and isinstance(value, str):
                datetime.datetime.strptime(value, self.date_format).date()
                setattr(instance, self.name, datetime.datetime.strptime(value, self.date_format).date())
        except ValueError:
            # raise ValueError('Incorrect date format: must be DD.MM.YYYY')
            logging.error(f'Validation Error: Attribute {self.name[1:]} must be str in DD.MM.YYYY format;')


class EmailField(CharField):

    def __init__(self, required, nullable, name='email'):
        super().__init__(required, nullable, name='email')
        self.name = "_" + 'email'

    def __set__(self, instance, value):
        if value and isinstance(value, str):
            if '@' not in value:
                # raise ValueError('Must contains @')
                logging.error(f'Validation Error: attribute {self.name[1:]} must contains @;')
            super().__set__(instance, value)


class PhoneField(CharField):

    def __init__(self, required, nullable, name='phone'):
        super().__init__(required, nullable, name='phone')
        self.name = "_" + 'phone'

    def __set__(self, instance, value):
        if value:
            if not (isinstance(value, str) or isinstance(value, int)):
                # raise TypeError("Must be a str or an int")
                logging.error(f"Validation Error: attribute {self.name[1:]} Must be a str or an int;")
            elif len(str(value)) != 11:
                # raise ValueError("It must contains 11 symbols")
                logging.error(f"Validation Error: attribute {self.name[1:]} must contains 11 symbols;")
            elif not str(value).startswith('7'):
                # raise ValueError("It must starts with 7")
                logging.error(f"Validation Error: attribute {self.name[1:]} must starts with 7;")
            setattr(instance, self.name, value)


class BirthDayField(DateField):
    def __init__(self, required, nullable, name='birthday'):
        super().__init__(required, nullable, name='birthday')
        self.name = "_" + 'birthday'

    def __set__(self, instance, value):
        super().__set__(instance, value)
        try:
            date_birth = datetime.datetime.strptime(value, self.date_format).date()
            if date_birth.replace(year=date_birth.year + 70) < datetime.datetime.now().date():
                # raise ValueError('Age over 70 years!')
                logging.error('Validation Error: Age over 70 years!;')
            setattr(instance, self.name, date_birth)
        except:
            # logging.error(f'Validation Error: Attribute {self.name[1:]} must be str in DD.MM.YYYY format;')
            pass


class GenderField(object):
    def __init__(self, required, nullable, name='gender', default=None):
        self.name = "_" + name
        self.type = int
        self.values = GENDERS
        self.required = required
        self.nullable = nullable
        self.default = default

    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)

    def __set__(self, instance, value):
        if self.required:
            if value is None:
                # raise ValueError(f'attribute {self.name[1:]} is required')
                logging.error(f'Validation Error: attribute {self.name[1:]} is required;')
            if not self.nullable and not value:
                # raise ValueError(f"attribute {self.name[1:]} can't be null")
                logging.error(f"Validation Error: attribute {self.name[1:]} can't be null;")
        if value and not isinstance(value, self.type):
            logging.error(f'Validation Error: attribute {self.name[1:]} must be an int;')
        if isinstance(value, self.type) and value not in self.values:
            # raise TypeError('Must be 0, 1 or 2')
            logging.error(f'Validation Error: attribute {self.name[1:]} must be in {GENDERS};')
        setattr(instance, self.name, value)


class ArgumentsField(object):
    def __init__(self, required, nullable, name='', default=None):
        self.name = "_" + name
        self.type = dict
        self.required = required
        self.nullable = nullable
        self.default = default
    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)
    def __set__(self, instance, value):
        if self.required:
            if value is None:
                # raise ValueError(f'attribute {self.name[1:]} is required')
                logging.error(f'Validation Error: attribute {self.name[1:]} is required;')
            if not self.nullable and not value:
                # raise ValueError(f"attribute {self.name[1:]} can't be null")
                logging.error(f"Validation Error: attribute {self.name[1:]} can't be null;")
        if not isinstance(value, self.type):
            # raise TypeError('Must be a dict')
            logging.error(f'Validation Error: attribute {self.name[1:]} must be a dict;')
        setattr(instance, self.name, value)


class ClientIDsField(object):
    def __init__(self, required, nullable, name='', default=None):
        self.name = "_" + name
        self.type = list
        self.required = required
        self.nullable = nullable
        self.default = default

    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)

    def __set__(self, instance, value):
        if self.required:
            if value is None:
                # raise ValueError(f'attribute {self.name[1:]} is required')
                logging.error(f'Validation Error: attribute {self.name[1:]} is required;')
            if not self.nullable and not value:
                # raise ValueError(f"attribute {self.name[1:]} can't be null")
                logging.error(f"Validation Error: attribute {self.name[1:]} can't be null;")
        if not isinstance(value, self.type):
            # raise TypeError('Must be a list')
            logging.error(f'Validation Error: attribute {self.name[1:]} must be a list;')
        err = 0
        for i in value:
            if not isinstance(i, int):
                err += 1
        if err:
            # raise TypeError("Client id's must be integer")
            logging.error("Validation Error: Client id's must be integer;")
        setattr(instance, self.name, value)


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True, nullable=False, name='client_ids')
    date = DateField(required=False, nullable=True, name='date')


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True, name='first_name')
    last_name = CharField(required=False, nullable=True, name='last_name')
    email = EmailField(required=False, nullable=True, name='email')
    phone = PhoneField(required=False, nullable=True, name='phone')
    birthday = BirthDayField(required=False, nullable=True, name='birthday')
    gender = GenderField(required=False, nullable=True, name='gender')


class MethodRequest(object):
    account = CharField(required=False, nullable=True, name='account')
    login = CharField(required=True, nullable=True, name='login')
    token = CharField(required=True, nullable=True, name='token')
    arguments = ArgumentsField(required=True, nullable=True, name='arguments')
    method = CharField(required=True, nullable=True, name='method')

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H").encode('utf-8') + ADMIN_SALT.encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512(str(request.account).encode('utf-8') + str(request.login).encode('utf-8') + SALT.encode('utf-8')).hexdigest()
    # print(f'digest: {digest}')
    if digest == request.token:
        return True
    return False


def method_handler(request, context, log_file_name, router, store):
    response, code = None, None
    logging.info(f'context: {context}')
    new_request = MethodRequest()
    # Field validation
    new_request.account = request.get('account')
    new_request.login = request.get('login')
    new_request.method = request.get('method')
    new_request.token = request.get('token')
    new_request.arguments = request.get('arguments')
    # Auth
    check_result = check_auth(new_request)
    if check_result:
        # if request.get('method') == 'online_score':
        if new_request.method == 'online_score':
            if new_request.login == 'admin':
                code, response = OK, {"score": 42}
                # result = {"code": OK, "response": {"score": 42}}
            else:
                online_score_request = OnlineScoreRequest()
                if request.get('arguments'):
                    online_score_request.phone = request.get('arguments').get('phone')
                    online_score_request.email = request.get('arguments').get('email')
                    online_score_request.first_name = request.get('arguments').get('first_name')
                    online_score_request.last_name = request.get('arguments').get('last_name')
                    online_score_request.birthday = request.get('arguments').get('birthday')
                    online_score_request.gender = request.get('arguments').get('gender')

                if not (online_score_request.phone and online_score_request.email) and \
                        not (online_score_request.first_name and online_score_request.last_name) and \
                        not (online_score_request.gender != "" and online_score_request.birthday):
                    logging.error(
                        'Validation Error: At least one pair phone-email, first name-last name, gender-birthday should be filled;')
        # elif request.get('method') == 'clients_interests':
        elif new_request.method == 'clients_interests':
            clients_interests = ClientsInterestsRequest()
            if request.get('arguments'):
                clients_interests.client_ids = request.get('arguments').get('client_ids')
                clients_interests.date = request.get('arguments').get('date')
        #  Check validation errors
        err_msg = ''
        with open(log_file_name) as f:
            for num, line in enumerate(f, 1):
                if context["request_id"] in line:
                    line_start = num
                    break
            # lines = f.readlines()[need_line:]
            try:
                for num, line in enumerate(f, line_start + 1):
                    if 'Validation Error:' in line:
                        # with open('api_log.log', encoding='utf-8') as f:
                        #     for line in f:
                        #         if 'Validation Error:' in line:
                        err_msg += line[line.rfind('Error:') + len('Error:') + 1:].replace('\n', ' ')
            except:
                logging.exception('Errors with getting info from log file')
        if err_msg:
            code, response = INVALID_REQUEST, err_msg[:-2]
            # result = {"code": INVALID_REQUEST, "error": err_msg}
        else:
            # Calculation
            # context = dict.fromkeys(['has'])
            try:
                # if new_request.method == 'online_score':
                if new_request.method == 'online_score' and new_request.login != 'admin':
                    # score = scoring.get_score(online_score_request)
                    score = router.get(new_request.method)(store, online_score_request)
                    code, response = OK, {"score": score}
                    context['has'] = [k for k, v in new_request.arguments.items() if v != ""]
                # elif new_request.method == 'clients_interests':
                elif new_request.method == 'clients_interests':
                    interests_list = {}
                    context['nclients'] = len(clients_interests.client_ids)

                    for id in clients_interests.client_ids:
                        interests_list[str(id)] = router.get(new_request.method)(store, id)
                    code, response = OK, interests_list
            except:
                code = INTERNAL_ERROR
    else:
        code = FORBIDDEN
        logging.info(f'Authentication for {new_request.account} is failed')
    return response, code


def main_http_handler(log_file_name):
    class MainHTTPHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super(MainHTTPHandler, self).__init__(*args, **kwargs)

        def get_request_id(self, headers):
            return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

        def do_POST(self):
            router = {
                "online_score": scoring.get_score,
                "clients_interests": scoring.get_interests
            }
            store = None
            response, code = {}, OK
            context = {"request_id": self.get_request_id(self.headers)}
            request = None
            try:
                data_string = self.rfile.read(int(self.headers['Content-Length']))
                request = json.loads(data_string)
            except:
                code = BAD_REQUEST

            if request:
                path = self.path.strip("/")
                logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
                response = None
                if path in router:
                    response, code = method_handler(request, context, log_file_name, router, store)
                else:
                    code = NOT_FOUND

                if code not in ERRORS:
                    r = {"response": response, "code": code}
                else:
                    r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}

            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if code not in ERRORS:
                r = {"response": response, "code": code}
            else:
                r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
            context.update(r)
            logging.info(context)
            self.wfile.write(json.dumps(r).encode('utf-8'))
    return MainHTTPHandler

if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8000)
    op.add_option("-l", "--log", action="store", default="api_log.log")
    (opts, args) = op.parse_args()

    logging.basicConfig(
        filename=opts.log,
        # filemode='w',
        format="%(asctime)s %(levelname).1s %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.INFO
    )
    MainHandler = main_http_handler(opts.log)
    server = HTTPServer(('127.0.0.1', 8000), MainHandler)
    logging.info("Starting server at %s" % opts.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.debug('Server is down')
    server.server_close()




