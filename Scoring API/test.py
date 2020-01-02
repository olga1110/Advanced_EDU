import hashlib
import datetime
import functools
import logging
import unittest
import uuid

import api
import scoring

logging.basicConfig(
    filename='api_log.log',
    # filemode='w',
    format="%(asctime)s %(levelname).1s %(message)s",
    datefmt='%Y.%m.%d %H:%M:%S',
    level=logging.INFO
)

def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {"request_id": uuid.uuid4().hex}
        self.headers = {}
        self.store = None
        self.log_file_name = 'api_log.log'
        self.router = {
            "online_score": scoring.get_score,
            "clients_interests": scoring.get_interests
        }

    def get_response(self, request):
        return api.method_handler(request, self.context, self.log_file_name, self.router, self.store)

    # def set_valid_auth(self, request):
    #     if request.get("login") == api.ADMIN_LOGIN:
    #         request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H").encode('utf-8') + api.ADMIN_SALT.encode('utf-8')).hexdigest()
    #     else:
    #         msg = request.get("account", "").encode('utf-8') + request.get("login", "").encode('utf-8') + api.SALT.encode('utf-8')
    #         request["token"] = hashlib.sha512(msg).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({"token": "f6e434dd2d376a3766c96a39d47fcfdbec31c720898de51ce9cbd15cc7e7d4b0e7c79c550824f806c5604db752ff54e0e24100ed4da2409291eef1d906e01e54"})
        self.assertEqual(api.INVALID_REQUEST, code)

    @cases([
        {},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ])
    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)


    @cases([
        {"account": "test", "login": "h&f", "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0",
         "arguments": {}},
        {"account": "test", "login": "h&f", "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0",
         "arguments": []},
        {"token": "f6e434dd2d376a3766c96a39d47fcfdbec31c720898de51ce9cbd15cc7e7d4b0e7c79c550824f806c5604db752ff54e0e24100ed4da2409291eef1d906e01e54",
            "arguments": []},
        {"account": "test",
         "token": "9232555e9ad0f1ff79da93b9c82520b48f70057a501e9a2a26a415036d9df2a550698cf4cd3c169e36f22fa3fc5b7566a34bcfff38337243eec94d4c91ea043e",
         "arguments": {}}
    ])
    def test_invalid_required_request(self, request):
        # self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertTrue(len(response))

    @cases([
        {},
        {"phone": "7917500204", "email": "stupnikov@otus.ru"},
        {"phone": 7917500204, "email": "stupnikov@otus.ru"},
        {"phone": [79175002040], "email": "stupnikov@otus.ru"},
        {"phone": 89175002040, "email": "stupnikov@otus.ru"},
        {"email": "stupnikov_otus.ru", "phone": 79175002040},
        {"email": 123, "phone": "79175002040"},
        {"first_name": 123, "last_name": "123"},
        {"first_name": "123", "last_name": 123},
        {"first_name": [], "last_name": ()},
        {"birthday": "01.01.90", "gender": 1},
        {"birthday": 90, "gender": 1},
        {"birthday": [1, 2, 3], "gender": 1},
        {"birthday": "01.01.1990", "gender": '1'},
        {"birthday": "01.01.1990", "gender": 4},
        {"birthday": "01.01.1990", "gender": [2]},
        {"gender": 2, "first_name": 123,  "phone": 79175002040},
    ])
    def test_invalid_score_request(self, arguments):
        request = {"account": "test", "login": "h&f", "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0", "method": "online_score", "arguments": arguments}
        # self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
        {"first_name": "a", "last_name": "b", "phone": "", "email": "", "gender": "", "birthday": ""},
    ])
    def test_ok_score_request(self, arguments):
        request = {"account": "test", "login": "h&f",
                   "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0",
                   "method": "online_score", "arguments": arguments}
        # self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, arguments)
        score = response.get("score")
        self.assertTrue(isinstance(score, (int, float)) and score >= 0, arguments)
        # self.assertEqual(sorted(self.context["has"]), sorted(arguments.keys()))
        self.assertEqual(sorted(self.context["has"]), sorted([k for k, v in arguments.items() if v != ""]))

    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_ok_interests_request(self, arguments):
        request = {"account": "test", "login": "h&f",
                   "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0",
                   "method": "clients_interests", "arguments": arguments}
        # self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, arguments)
        self.assertEqual(len(arguments["client_ids"]), len(response))
        self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, str) for i in v)
                        for v in response.values()))
        self.assertEqual(self.context.get("nclients"), len(arguments["client_ids"]))

    @cases([
        {},
        {"date": "20.07.2017"},
        {"date": ""},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
        {"client_ids": []}
    ])
    def test_invalid_interests_request(self, arguments):
        request = {"account": "test", "login": "h&f",
                   "token": "05eee6fdbd79f9ed11c4976b5148e01e8982b6729e365d9c6a1e50af31d217ff87ffcd81c97040f7c3840dd1e699af889fac0eaed561dadc0a0aa54aae4ff8a0",
                   "method": "clients_interests", "arguments": arguments}
        # self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))


if __name__ == "__main__":
    unittest.main()
