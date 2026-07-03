from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from config.middleware import AuthenticationMiddleware, MySessionMiddleware
from app.models import Session
from app.session import SessionStore
from django.contrib.auth import get_user_model

User = get_user_model()


class SessionMiddlewareTests(TestCase):
    def get_response(self, request):
        from django.http import HttpResponse

        return HttpResponse("OK")

    def test_creates_session_for_first_request(self):
        middleware = MySessionMiddleware(self.get_response)

        request = RequestFactory().get("/")
        request.COOKIES = {}

        response = middleware(request)

        self.assertIn("sessionid", response.cookies)

        session_key = response.cookies["sessionid"].value

        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

    def test_reuses_existing_session(self):
        session = Session.create()

        middleware = MySessionMiddleware(self.get_response)

        request = RequestFactory().get("/")
        request.COOKIES = {
            "sessionid": session.session_key,
        }

        response = middleware(request)

        self.assertEqual(
            response.cookies["sessionid"].value,
            session.session_key,
        )

    def test_session_persists_data(self):
        session = Session.create()

        middleware = MySessionMiddleware(self.get_response)

        request = RequestFactory().get("/")
        request.COOKIES = {
            "sessionid": session.session_key,
        }

        middleware(request)

        request.session["foo"] = "bar"
        request.session.save()

        request2 = RequestFactory().get("/")
        request2.COOKIES = {
            "sessionid": session.session_key,
        }

        middleware(request2)

        self.assertEqual(
            request2.session["foo"],
            "bar",
        )


class AuthenticationMiddlewareTests(TestCase):
    def test_adds_user_attribute(self):
        request = RequestFactory().get("/")

        request.session = {}

        AuthenticationMiddleware(lambda r: None).process_request(request)

        self.assertTrue(hasattr(request, "user"))

    def test_default_user_is_anonymous(self):
        request = RequestFactory().get("/")

        request.session = {}

        AuthenticationMiddleware(lambda r: None).process_request(request)

        self.assertIsInstance(request.user, AnonymousUser)
        self.assertFalse(request.user.is_authenticated)


class AuthenticationIntegrationTests(TestCase):
    def test_authenticated_user_loaded_from_session(self):
        user = User.objects.create_user(
            username="alice",
            password="secret",
        )

        session = Session.create()

        store = SessionStore(session)
        store["_auth_user_id"] = str(user.pk)
        store["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
        store.save()

        request = RequestFactory().get("/")
        request.COOKIES = {
            "sessionid": session.session_key,
        }

        MySessionMiddleware(lambda request: HttpResponse("OK"))(request)
        AuthenticationMiddleware(lambda r: None).process_request(request)

        self.assertTrue(request.user.is_authenticated)
        self.assertEqual(request.user.pk, user.pk)
