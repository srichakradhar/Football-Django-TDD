from django.test import TestCase
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from . import views
from .models import Team, Players, AdminProfile, Mappings, Viewer, Bookings
from difflib import SequenceMatcher
import json
from django.contrib.auth.hashers import check_password, make_password


class AllNewFeatureTests(TestCase):
    def setUp(self):
        client = Client()
        self.viewer_payload = {'name': 'viewer1', 'password' : 'test1234'}
        Mappings.objects.create(name="Team 1", category="Semi-Final 1")
    #     self.team_payload = {'name': 'team1', 'password' : 'test1234', 'country':'India', 'coach':'testcoach'}
    #     self.team2_payload = {'name': 'team2', 'password' : 'test1234', 'country':'Thailand', 'coach':'testcoach'}
    #     self.team_login_payload = {'name': 'team1', 'password' : 'test1234'}
    #     self.team_login2_payload = {'name': 'team2', 'password' : 'test1234'}
    #     self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
    #     response = self.client.post(
    #         reverse('Register-Team'),
    #         data = json.dumps(self.team_payload),
    #         content_type = 'application/json'
    #         )

    #     login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
    #     token = login.data['token'].decode('utf-8')
    #     headers = {'HTTP_AUTHORIZATION': token}
    #     register = self.client.post(
    #         reverse('Register-Player'),
    #         data = json.dumps(self.valid_player_payload),
    #         content_type = 'application/json',
    #         **headers
    #         )

    #     other_team = self.client.post(
    #         reverse('Register-Team'),
    #         data = json.dumps(self.team2_payload),
    #         content_type = 'application/json'
    #         )
    #     Mappings.objects.create(id=1, name="",category="Semi-Final 1")

    def test_viewer_registration(self):
        self.viewer_payload1 = {'name': 'viewer1', 'password' : 'test1234'}
        response = self.client.post(
            reverse('Register-Viewer'),
            data = json.dumps(self.viewer_payload1),
            content_type = 'application/json'
            )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, {'name': 'viewer1'})

    def test_viewer_registration_failed(self):
        self.viewer_payload1 = {'name': 'viewer1', 'password' : 'test1234'}
        response = self.client.post(
            reverse('Register-Viewer'),
            data = json.dumps(self.viewer_payload1),
            content_type = 'application/json'
            )

        self.viewer_payload1 = {'name': 'viewer1', 'password' : 'test1234'}
        response = self.client.post(
            reverse('Register-Viewer'),
            data = json.dumps(self.viewer_payload1),
            content_type = 'application/json'
            )
        self.assertEquals(response.status_code, 400)
        s = SequenceMatcher(lambda x: x == " ", response.data['Message'].strip(), "Registration failed")
        match = round(s.ratio(), 3)
        self.assertGreaterEqual(match, 0.8)

    def test_viewer_login(self):
        register = self.client.post(
            reverse('Register-Viewer'),
            data = json.dumps(self.viewer_payload),
            content_type = 'application/json'
            )
        login = self.client.post(
            reverse('Login-Viewer'),
            data = json.dumps(self.viewer_payload),
            content_type = 'application/json'
            )

        self.assertEquals(login.status_code, 200)
        self.assertIn('token', login.data)
        self.assertIn('viewer', login.data)
        # self.assertEquals(login.data['team'] , {'country': 'India', 'name': 'team1', 'coach': 'testcoach'})

    def test_view_matches_success(self):
        register = self.client.post(reverse('Register-Viewer'),    data = json.dumps(self.viewer_payload),    content_type = 'application/json')
        login = self.client.post(reverse('Login-Viewer'),data = json.dumps(self.viewer_payload),content_type = 'application/json')
        self.assertEquals(login.status_code, 200)

        token = login.data['token'].decode('utf-8')
        headers = {"HTTP_AUTHORIZATION":token}
        
        matches = self.client.get(
            reverse('View-Matches'),
            # data = json.dumps(self.viewer_payload),
            content_type = 'application/json',
            **headers
            )
        # matches = self.client.get(
        #     reverse('View-Matches'),
        #     data = json.dumps(self.viewer_payload),
        #     content_type = 'application/json'
        #     )
        self.assertEquals(matches.status_code, 200)
        self.assertEquals(matches.data, [{'name': 'Team 1', 'category': 'Semi-Final 1'}])

    def test_view_mathces_without_login(self):
        matches = self.client.get(
            reverse('View-Matches'),
            # data = json.dumps(self.viewer_payload),
            content_type = 'application/json',
            
            )
        # matches = self.client.get(
        #     reverse('View-Matches'),
        #     data = json.dumps(self.viewer_payload),
        #     content_type = 'application/json'
        #     )
        self.assertEquals(matches.status_code, 400)
        s = SequenceMatcher(lambda x: x == " ", matches.data['Message'].strip(), "Token required")
        match = round(s.ratio(), 3)
        self.assertGreaterEqual(match, 0.8)


    def test_book_ticket_without_login(self):
        # register = self.client.post(reverse('Register-Viewer'),    data = json.dumps(self.viewer_payload),    content_type = 'application/json')
        # login = self.client.post(reverse('Login-Viewer'),data = json.dumps(self.viewer_payload),content_type = 'application/json')
        # self.assertEquals(login.status_code, 200)

        # token = login.data['token'].decode('utf-8')
        # headers = {"HTTP_AUTHORIZATION":token}
        
        book = self.client.post(
            reverse('Book-Ticket', kwargs={'match_id':1}),
            content_type = 'application/json'
            )
        self.assertEquals(book.status_code, 400)
        s = SequenceMatcher(lambda x: x == " ", book.data['Message'].strip(), "Could not verify")
        match = round(s.ratio(), 3)
        self.assertGreaterEqual(match, 0.8)

    def test_book_tickets_with_login(self):
        register = self.client.post(reverse('Register-Viewer'),    data = json.dumps(self.viewer_payload),    content_type = 'application/json')
        login = self.client.post(reverse('Login-Viewer'),data = json.dumps(self.viewer_payload),content_type = 'application/json')
        self.assertEquals(login.status_code, 200)

        token = login.data['token'].decode('utf-8')
        headers = {"HTTP_AUTHORIZATION":token}

        book = self.client.post(
            reverse("Book-Ticket", kwargs={"match_id":1}),
            content_type = "application/json",
            **headers
            )
        self.assertEquals(book.status_code, 200)
        s = SequenceMatcher(lambda x: x == " ", book.data['Message'].strip(), "Ticket booked successfully")
        match = round(s.ratio(), 3)
        self.assertGreaterEqual(match, 0.8)

    def test_view_bookings_without_login(self):
        bookings = self.client.get(
            reverse("View-Bookings"), 
            content_type = 'application/json',
            )
        self.assertEquals(bookings.status_code, 400)
        s = SequenceMatcher(lambda x: x == " ", bookings.data['Message'].strip(), "Could not verify")
        match = round(s.ratio(), 3)
        self.assertGreaterEqual(match, 0.8)

    def test_view_bookings_with_login_success(self):
        register = self.client.post(reverse('Register-Viewer'),    data = json.dumps(self.viewer_payload),    content_type = 'application/json')
        login = self.client.post(reverse('Login-Viewer'),data = json.dumps(self.viewer_payload),content_type = 'application/json')
        self.assertEquals(login.status_code, 200)

        token = login.data['token'].decode('utf-8')
        headers = {"HTTP_AUTHORIZATION":token}
        
        book = self.client.post(
            reverse("Book-Ticket", kwargs={"match_id":1}),
            content_type = "application/json",
            **headers
            )
        self.assertEquals(book.status_code, 200)
        
        bookings = self.client.get(
            reverse("View-Bookings"), 
            content_type = 'application/json',
            **headers
            )
        self.assertEquals(bookings.status_code, 200)
        self.assertEquals(bookings.data, [{'matchId': 1, 'bookingMadeBy': 1}])
