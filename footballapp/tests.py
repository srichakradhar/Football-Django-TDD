from django.test import TestCase
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from . import views
from .models import Team, Players, AdminProfile, Mappings
from difflib import SequenceMatcher
import json
from django.contrib.auth.hashers import check_password, make_password


class AllModelsTests(TestCase):
	def setUp(self):
		client = Client()
		self.team_payload = {'name': 'team1', 'password' : 'test1234', 'country':'India', 'coach':'testcoach'}
		self.team2_payload = {'name': 'team2', 'password' : 'test1234', 'country':'Thailand', 'coach':'testcoach'}
		self.team_login_payload = {'name': 'team1', 'password' : 'test1234'}
		self.team_login2_payload = {'name': 'team2', 'password' : 'test1234'}
		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		response = self.client.post(
			reverse('Register-Team'),
			data = json.dumps(self.team_payload),
			content_type = 'application/json'
			)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)

		other_team = self.client.post(
			reverse('Register-Team'),
			data = json.dumps(self.team2_payload),
			content_type = 'application/json'
			)
		Mappings.objects.create(id=1, name="",category="Semi-Final 1")

	def test_team_registraion(self):
		self.team_payload1 = {'name': 'team3', 'password' : 'test1234', 'country':'Sri Lanka', 'coach':'testcoach'}
		response = self.client.post(
			reverse('Register-Team'),
			data = json.dumps(self.team_payload1),
			content_type = 'application/json'
			)

		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.data, {'country': 'Sri Lanka', 'coach': 'testcoach', 'name': 'team3'})

	def test_team_failed_registration(self):
		response = self.client.post(
			reverse('Register-Team'),
			data = json.dumps(self.team_payload),
			content_type = 'application/json'
			)

		self.assertEquals(response.status_code, 400)
		s = SequenceMatcher(lambda x: x == " ", response.data['Message'].strip(), "Registration failed")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	def test_login_team(self):
		login = self.client.post(
			reverse('Login-Team'),
			data = json.dumps(self.team_login_payload),
			content_type = 'application/json'
			)

		self.assertEquals(login.status_code, 200)
		self.assertIn('token', login.data)
		self.assertIn('team', login.data)
		self.assertEquals(login.data['team'] , {'country': 'India', 'name': 'team1', 'coach': 'testcoach'})


	def test_teams_views(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		
		token = login.data['token'].decode('utf-8')
		# self.headers = {'Authorization': token}
		headers = {'HTTP_AUTHORIZATION': token}
		views = self.client.get(
			reverse('View-Team'),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(views.status_code, 200)
		self.assertEquals(views.data, [{'country': 'India', 'coach': 'testcoach', 'name': 'team1', 'id': 1}, {'country': 'Thailand', 'coach': 'testcoach', 'name': 'team2', 'id': 2}])

	def test_teams_view_without_token(self):
		headers = {}
		views = self.client.get(
			reverse('View-Team'),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(views.status_code, 400)
		s = SequenceMatcher(lambda x: x == " ", views.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	def test_teams_update(self):
		team = Team.objects.all()
		self.assertEquals(team[0].coach, 'testcoach')

		self.update_payload = {'coach':'testcoachupdate'}
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		views = self.client.patch(
			reverse('Update-Team'),
			data = json.dumps(self.update_payload),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(views.status_code, 200)
		s = SequenceMatcher(lambda x: x == " ", views.data['Message'].strip(), "Update successful")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		team = Team.objects.all()
		self.assertEquals(team[0].coach, 'testcoachupdate')

	def test_player_register_success(self):
		player = Players.objects.all()
		self.assertEquals(len(player), 1)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		

		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(register.status_code,200)
		s = SequenceMatcher(lambda x: x == " ", register.data['Message'].strip(), "Registraion successful")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		player = Players.objects.all()
		self.assertEquals(len(player), 2)

	def test_player_register_failed_without_token(self):
		player = Players.objects.all()
		self.assertEquals(len(player), 1)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		

		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')
		
		# headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json'
			)

		self.assertEquals(register.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", register.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		player = Players.objects.all()
		self.assertEquals(len(player), 1)

	def test_player_update_success(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		

		self.valid_playerupdate_payload = { 'name':'playerupdated', 'age':25, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')

		self.assertEquals(Players.objects.all()[0].name, 'player')
		self.assertEquals(Players.objects.all()[0].age, 20)

		headers = {"HTTP_AUTHORIZATION":token}
		update = self.client.patch(
			reverse('Update-player', kwargs={'id':1}),
			data = json.dumps(self.valid_playerupdate_payload),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(update.status_code,200)
		# self.assertEquals(update.data,'Update successful')
		s = SequenceMatcher(lambda x: x == " ", update.data['Message'].strip(), "Update successful")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)
		self.assertEquals(Players.objects.all()[0].age, 25)
		self.assertEquals(Players.objects.all()[0].name,'playerupdated')

	def test_player_update_failed_without_token(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		

		self.valid_playerupdate_payload = { 'name':'playerupdated', 'age':25, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')

		self.assertEquals(Players.objects.all()[0].name, 'player')

		# headers = {"HTTP_AUTHORIZATION":token}
		update = self.client.patch(
			reverse('Update-player', kwargs={'id':1}),
			data = json.dumps(self.valid_playerupdate_payload),
			content_type = 'application/json'
			)
		self.assertEquals(update.status_code,400)
		# self.assertEquals(update.data,'Update successful')
		s = SequenceMatcher(lambda x: x == " ", update.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)
		self.assertEquals(Players.objects.all()[0].name,'player')

	def test_player_view_success(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)		

		token = login.data['token'].decode('utf-8')
		headers = {"HTTP_AUTHORIZATION":token}
		views = self.client.get(
			reverse('View-Player'),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(views.status_code,200)
		self.assertEquals(views.data,[{'name': 'player', 'type': 'Goal Keeper', 'id': 1, 'age': 20, 'goalsScored': 10, 'noOfMatches': 10, 'inEleven': False}])
	

	def test_player_view_failed(self):
		views = self.client.get(
			reverse('View-Player'),
			content_type = 'application/json',
			)
		self.assertEquals(views.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", views.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	def test_player_delete_success(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)	

		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(len(Players.objects.all()),2)

		delete = self.client.delete(
			reverse('Delete-Player', kwargs={'id':2}),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(delete.status_code,204)
		self.assertEquals(len(Players.objects.all()),1)

	def test_player_delete_failed(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)	

		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(len(Players.objects.all()),2)

		delete = self.client.delete(
			reverse('Delete-Player', kwargs={'id':20}),
			content_type = 'application/json',
			**headers
			)
		self.assertEquals(delete.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", delete.data['Message'].strip(), "Couldn't delete")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		self.assertEquals(len(Players.objects.all()),2)

	
	def test_delete_player_without_token(self):
		self.assertEquals(len(Players.objects.all()),1)

		delete = self.client.delete(
			reverse('Delete-Player', kwargs={'id':20}),
			content_type = 'application/json'
			)
		self.assertEquals(delete.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", delete.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		self.assertEquals(len(Players.objects.all()),1)

	def test_delete_all_players_success(self):
		self.assertEquals(len(Players.objects.all()),1)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		register = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(len(Players.objects.all()),2)

		delete_all = self.client.delete(
			reverse('Delete-All-Players'),
				**headers
			)

		self.assertEquals(delete_all.status_code, 204)


		delete_all = self.client.delete(
			reverse('Delete-All-Players'),
				**headers
			)

		self.assertEquals(delete_all.status_code, 400)
		s = SequenceMatcher(lambda x: x == " ", delete_all.data['Message'].strip(), "Couldn't delete")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	def test_delete_all_players_failed(self):
		delete_all = self.client.delete(
			reverse('Delete-All-Players')
			)

		self.assertEquals(delete_all.status_code, 400)
		s = SequenceMatcher(lambda x: x == " ", delete_all.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	def test_view_mappings(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		self.assertEquals(login.status_code, 200)	
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION': token}
		mappings = self.client.get(
			reverse('View-Mappings'),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(mappings.data,[{'category': 'Semi-Final 1', 'id': 1, 'name': ''}])
		self.assertEquals(mappings.status_code, 200)

	def test_view_mappings_without_login(self):
		mappings = self.client.get(
			reverse('View-Mappings'),
			content_type = 'application/json',
			)

	
		self.assertEquals(mappings.status_code, 400)
		s = SequenceMatcher(lambda x: x == " ", mappings.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

class AdminProfileActionsTests(TestCase):
	def setUp(self):
		client = Client()
		self.team_payload = {'name': 'team1', 'password' : 'test1234', 'country':'India', 'coach':'testcoach'}
		self.team2_payload = {'name': 'team2', 'password' : 'test1234', 'country':'Sri Lanka', 'coach':'testcoach'}
		self.admin_payload = {'name': 'admin', 'password' : 'test1234'}
		self.team_login_payload = {'name': 'team1', 'password' : 'test1234'}
		self.team_login2_payload = {'name': 'team2', 'password' : 'test1234'}
		self.valid_player_payload = { 'name':'player', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		self.valid_player2_payload = { 'name':'player2', 'age':20, 'type':"Goal Keeper", 'noOfMatches': 10, 'goalsScored':10}
		
		register_admin = self.client.post(
			reverse("Register-Admin"),
			data = json.dumps(self.admin_payload),
			content_type='application/json'
			)

		register_team = self.client.post(
			reverse("Register-Team"),
			data = json.dumps(self.team_payload),
			content_type='application/json'
			)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION': token}

		register_player = self.client.post(
			reverse('Register-Player'),
			data = json.dumps(self.valid_player_payload),
			content_type = 'application/json',
			**headers
			)

		other_team = self.client.post(
			reverse('Register-Team'),
			data = json.dumps(self.team2_payload),
			content_type = 'application/json'
			)
		Mappings.objects.create(id=1, name="",category="Semi-Final 1")

	def test_update_mappings_by_admin(self):
		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		
		self.valid_update_mapping_payload = {'name':'Team 1'}
		headers = {'HTTP_AUTHORIZATION': token}
		
		viewmappings = self.client.get(reverse('View-Mappings'),**headers)

		self.assertEquals(viewmappings.data,[{'category': 'Semi-Final 1', 'id': 1, 'name': ''}] )
		# print(viewmappings.data)

		updatemapping = self.client.patch(
			reverse('Update-Mappings', kwargs={'id':1}),
			data = json.dumps(self.valid_update_mapping_payload),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(updatemapping.status_code,200)
		s = SequenceMatcher(lambda x: x == " ", updatemapping.data['Message'].strip(), "Update successful")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)


		viewmappings = self.client.get(reverse('View-Mappings'),**headers)
		self.assertEquals(viewmappings.data, [{'category': 'Semi-Final 1', 'id': 1, 'name': 'Team 1'}])

	def test_update_mappings_without_token(self):
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		
		self.valid_update_mapping_payload = {'name':'Team 1'}
		headers = {'HTTP_AUTHORIZATION': token}
		
		viewmappings = self.client.get(reverse('View-Mappings'),**headers)
		self.assertEquals(viewmappings.data,[{'category': 'Semi-Final 1', 'id': 1, 'name': ''}] )

		updatemappings = self.client.patch(
			reverse('Update-Mappings', kwargs={'id':1}),
			data = json.dumps(self.valid_update_mapping_payload),
			content_type = 'application/json'
			)

		self.assertEquals(updatemappings.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", updatemappings.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)



		viewmappings = self.client.get(reverse('View-Mappings'),**headers)
		self.assertEquals(viewmappings.data, [{'category': 'Semi-Final 1', 'id': 1, 'name': ''}])


		updatemappings = self.client.patch(
			reverse('Update-Mappings', kwargs={'id':100}),
			data = json.dumps(self.valid_update_mapping_payload),
			content_type = 'application/json',
			**headers
			)

		self.assertEquals(updatemappings.status_code,400)
		s = SequenceMatcher(lambda x: x == " ", updatemappings.data['Message'].strip(), "Not an admin")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)


	def test_register_player_by_admin(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),1)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		
		headers = {'HTTP_AUTHORIZATION':token}
		register_player = self.client.post(
			reverse('Register-Players-Admin', kwargs={'id':1}),
			data = json.dumps(self.valid_player2_payload),
			content_type='application/json',
			**headers
			)

		self.assertEquals(register_player.data,{'belongsTo': 1, 'age': 20, 'name': 'player2', 'goalsScored': 10, 'noOfMatches': 10, 'type': 'Goal Keeper'})
		self.assertEquals(register_player.status_code, 200)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),2)


	def test_update_player_by_admin(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals((player[0].name), "player")

		self.update_player = {"name":"playerupdated","age":35,"noOfMatches":100,"inEleven":True}
		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		update_player = self.client.post(
			reverse('Update-Players-Admin', kwargs={'id':1}),
			data = json.dumps(self.update_player),
			content_type='application/json',
			**headers
			)

		self.assertEquals(update_player.status_code,200)

		s = SequenceMatcher(lambda x: x == " ", update_player.data['Message'].strip(), "Update successful")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals((player[0].name), "playerupdated")



	def test_update_player_by_Admin_failure(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(player[0].name, "player")

		self.update_player = {"name":"playerupdated","age":35,"noOfMatches":100,"inEleven":True}
		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		update_player = self.client.post(
			reverse('Update-Players-Admin', kwargs={'id':100}),
			data = json.dumps(self.update_player),
			content_type='application/json',
			**headers
			)

		self.assertEquals(update_player.status_code,400)

		s = SequenceMatcher(lambda x: x == " ", update_player.data['Message'].strip(), "Not a valid id")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(player[0].name, "player")



	def test_update_player_without_token(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(player[0].name, "player")


		self.update_player = {"name":"playerupdated","age":35,"noOfMatches":100,"inEleven":True}
		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		update_player = self.client.post(
			reverse('Update-Players-Admin', kwargs={'id':1}),
			data = json.dumps(self.update_player),
			content_type='application/json'
			)

		self.assertEquals(update_player.status_code,400)

		s = SequenceMatcher(lambda x: x == " ", update_player.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(player[0].name, "player")


	def test_update_player_with_team_access(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals((player[0].name), "player")

		self.update_player = {"name":"playerupdated","age":35,"noOfMatches":100,"inEleven":True}
		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		update_player = self.client.post(
			reverse('Update-Players-Admin', kwargs={'id':1}),
			data = json.dumps(self.update_player),
			content_type='application/json',
			**headers
			)

		self.assertEquals(update_player.status_code,400)

		s = SequenceMatcher(lambda x: x == " ", update_player.data['Message'].strip(), "Not an admin")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals((player[0].name), "player")

	def test_delete_team_players_by_Admin(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),1)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		delete_player = self.client.delete(
			reverse('Delete-Players-Admin', kwargs={'id':1}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(delete_player.status_code,204)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),0)

	def test_delete_team_players_by_Admin_failed(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),1)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		delete_player = self.client.delete(
			reverse('Delete-Players-Admin', kwargs={'id':100}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(delete_player.status_code,400)

		s = SequenceMatcher(lambda x: x == " ", delete_player.data['Message'].strip(), "Couldn't delete")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

	
	def test_delete_all_players_by_admin(self):
		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),1)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		delete_player = self.client.delete(
			reverse('Delete-All-Players-Admin', kwargs={'id':1}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(delete_player.status_code,204)

		player = Players.objects.filter(belongsTo=1).all()
		self.assertEquals(len(player),0)

	def test_team_delete_by_Admin(self):
		team = Team.objects.all()
		self.assertEquals(len(team),2)
		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		delete_player = self.client.delete(
			reverse('Delete-Team-Admin', kwargs={'id':1}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(delete_player.status_code,204)

		team = Team.objects.all()
		self.assertEquals(len(team),1)


	def test_team_eleven_by_Admin(self):
		
		team = Team.objects.filter(id=2).first()
		player2 = Players.objects.create(id=21, name='player2', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player3 = Players.objects.create(id=31, name='player3', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player4 = Players.objects.create(id=41, name='player4', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player5 = Players.objects.create(id=51, name='player5', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player6 = Players.objects.create(id=61, name='player6', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player7 = Players.objects.create(id=71, name='player7', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player8 = Players.objects.create(id=81, name='player8', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player9 = Players.objects.create(id=91, name='player9', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player10 = Players.objects.create(id=10, name='player10', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player11 = Players.objects.create(id=11, name='player11', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player12 = Players.objects.create(id=12, name='player12', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		eleven_team = self.client.get(
			reverse('Eleven-Team-Admin', kwargs={'id':2}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(eleven_team.status_code,200)
		self.assertEquals(eleven_team.data['Message'],'')
		self.assertEquals(eleven_team.data['team11s'], [{'inEleven': True, 'name': 'player10', 'noOfMatches': 25, 'id': 10, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player11', 'noOfMatches': 25, 'id': 11, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player12', 'noOfMatches': 25, 'id': 12, 'age': 25, 'type': 'Goal Keeper', 'goalsScored': 25}, {'inEleven': True, 'name': 'player2', 'noOfMatches': 25, 'id': 21, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player3', 'noOfMatches': 25, 'id': 31, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player4', 'noOfMatches': 25, 'id': 41, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player5', 'noOfMatches': 25, 'id': 51, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player6', 'noOfMatches': 25, 'id': 61, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player7', 'noOfMatches': 25, 'id': 71, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player8', 'noOfMatches': 25, 'id': 81, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player9', 'noOfMatches': 25, 'id': 91, 'age': 25, 'type': 'Defender', 'goalsScored': 25}])

	def test_team_eleven_by_user(self):

		team = Team.objects.filter(id=2).first()
		player2 = Players.objects.create(id=21, name='player2', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player3 = Players.objects.create(id=31, name='player3', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player4 = Players.objects.create(id=41, name='player4', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player5 = Players.objects.create(id=51, name='player5', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player6 = Players.objects.create(id=61, name='player6', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player7 = Players.objects.create(id=71, name='player7', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player8 = Players.objects.create(id=81, name='player8', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player9 = Players.objects.create(id=91, name='player9', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player10 = Players.objects.create(id=10, name='player10', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player11 = Players.objects.create(id=11, name='player11', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player12 = Players.objects.create(id=12, name='player12', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login2_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		eleven_team = self.client.get(
			reverse('Eleven-Team'),
			content_type='application/json',
			**headers
			)

		self.assertEquals(eleven_team.status_code,200)
		self.assertEquals(eleven_team.data['Message'],'')
		self.assertEquals(eleven_team.data['team11s'], [{'inEleven': True, 'name': 'player10', 'noOfMatches': 25, 'id': 10, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player11', 'noOfMatches': 25, 'id': 11, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player12', 'noOfMatches': 25, 'id': 12, 'age': 25, 'type': 'Goal Keeper', 'goalsScored': 25}, {'inEleven': True, 'name': 'player2', 'noOfMatches': 25, 'id': 21, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player3', 'noOfMatches': 25, 'id': 31, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player4', 'noOfMatches': 25, 'id': 41, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player5', 'noOfMatches': 25, 'id': 51, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player6', 'noOfMatches': 25, 'id': 61, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player7', 'noOfMatches': 25, 'id': 71, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player8', 'noOfMatches': 25, 'id': 81, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player9', 'noOfMatches': 25, 'id': 91, 'age': 25, 'type': 'Defender', 'goalsScored': 25}])

	def test_team_eleven_by_user_without_token(self):
		team = Team.objects.filter(id=2).first()
		player2 = Players.objects.create(id=21, name='player2', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player3 = Players.objects.create(id=31, name='player3', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player4 = Players.objects.create(id=41, name='player4', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player5 = Players.objects.create(id=51, name='player5', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player6 = Players.objects.create(id=61, name='player6', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player7 = Players.objects.create(id=71, name='player7', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player8 = Players.objects.create(id=81, name='player8', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player9 = Players.objects.create(id=91, name='player9', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player10 = Players.objects.create(id=10, name='player10', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player11 = Players.objects.create(id=11, name='player11', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player12 = Players.objects.create(id=12, name='player12', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)

		login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login2_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		eleven_team = self.client.get(
			reverse('Eleven-Team'),
			content_type='application/json',
			)

		self.assertEquals(eleven_team.status_code,400)
		# self.assertEquals(eleven_team.data['Message'],'Token required')
		# self.assertEquals(eleven_team.data['team11s'], [{'inEleven': True, 'name': 'player10', 'noOfMatches': 25, 'id': 10, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player11', 'noOfMatches': 25, 'id': 11, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player12', 'noOfMatches': 25, 'id': 12, 'age': 25, 'type': 'Goal Keeper', 'goalsScored': 25}, {'inEleven': True, 'name': 'player2', 'noOfMatches': 25, 'id': 21, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player3', 'noOfMatches': 25, 'id': 31, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player4', 'noOfMatches': 25, 'id': 41, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player5', 'noOfMatches': 25, 'id': 51, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player6', 'noOfMatches': 25, 'id': 61, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player7', 'noOfMatches': 25, 'id': 71, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player8', 'noOfMatches': 25, 'id': 81, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player9', 'noOfMatches': 25, 'id': 91, 'age': 25, 'type': 'Defender', 'goalsScored': 25}])

		s = SequenceMatcher(lambda x: x == " ", eleven_team.data['Message'].strip(), "Token required")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)


	def test_team_eleven_by_Admin_failed_condition(self):
		
		team = Team.objects.filter(id=2).first()
		player2 = Players.objects.create(id=21, name='player2', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player3 = Players.objects.create(id=31, name='player3', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player4 = Players.objects.create(id=41, name='player4', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player5 = Players.objects.create(id=51, name='player5', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player6 = Players.objects.create(id=61, name='player6', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player7 = Players.objects.create(id=71, name='player7', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player8 = Players.objects.create(id=81, name='player8', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player9 = Players.objects.create(id=91, name='player9', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player10 = Players.objects.create(id=10, name='player10', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player11 = Players.objects.create(id=11, name='player11', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
		player12 = Players.objects.create(id=12, name='player12', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)

		login = self.client.post(reverse('Login-Admin'),data = json.dumps(self.admin_payload),content_type = 'application/json')
		token = login.data['token'].decode('utf-8')
		headers = {'HTTP_AUTHORIZATION':token}
		eleven_team = self.client.get(
			reverse('Eleven-Team-Admin', kwargs={'id':2}),
			content_type='application/json',
			**headers
			)

		self.assertEquals(eleven_team.status_code,200)
		# self.assertEquals(eleven_team.data['Message'],'')
		# self.assertEquals(eleven_team.data['team11s'], [{'inEleven': True, 'name': 'player10', 'noOfMatches': 25, 'id': 10, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player11', 'noOfMatches': 25, 'id': 11, 'age': 25, 'type': 'Defender', 'goalsScored': 25}, {'inEleven': True, 'name': 'player12', 'noOfMatches': 25, 'id': 12, 'age': 25, 'type': 'Goal Keeper', 'goalsScored': 25}, {'inEleven': True, 'name': 'player2', 'noOfMatches': 25, 'id': 21, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player3', 'noOfMatches': 25, 'id': 31, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player4', 'noOfMatches': 25, 'id': 41, 'age': 25, 'type': 'Mid-Fielder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player5', 'noOfMatches': 25, 'id': 51, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player6', 'noOfMatches': 25, 'id': 61, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player7', 'noOfMatches': 25, 'id': 71, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player8', 'noOfMatches': 25, 'id': 81, 'age': 25, 'type': 'Forwarder', 'goalsScored': 25}, {'inEleven': True, 'name': 'player9', 'noOfMatches': 25, 'id': 91, 'age': 25, 'type': 'Defender', 'goalsScored': 25}])
		self.assertEquals(eleven_team.data["team11s"], [{'noOfMatches': 25, 'goalsScored': 25, 'name': 'player10', 'inEleven': True, 'age': 25, 'id': 10, 'type': 'Defender'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player11', 'inEleven': True, 'age': 25, 'id': 11, 'type': 'Goal Keeper'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player12', 'inEleven': True, 'age': 25, 'id': 12, 'type': 'Goal Keeper'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player2', 'inEleven': True, 'age': 25, 'id': 21, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player3', 'inEleven': True, 'age': 25, 'id': 31, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player4', 'inEleven': True, 'age': 25, 'id': 41, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player5', 'inEleven': True, 'age': 25, 'id': 51, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player6', 'inEleven': True, 'age': 25, 'id': 61, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player7', 'inEleven': True, 'age': 25, 'id': 71, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player8', 'inEleven': True, 'age': 25, 'id': 81, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player9', 'inEleven': True, 'age': 25, 'id': 91, 'type': 'Defender'}])

		s = SequenceMatcher(lambda x: x == " ", eleven_team.data['Message'].strip(), "Playing eleven does not meet required condition")
		match = round(s.ratio(), 3)
		self.assertGreaterEqual(match, 0.8)

		def test_team_eleven_by_user_with_failed_condition(self):
	

			team = Team.objects.filter(id=2).first()
			player2 = Players.objects.create(id=21, name='player2', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player3 = Players.objects.create(id=31, name='player3', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player4 = Players.objects.create(id=41, name='player4', type='Mid-Fielder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player5 = Players.objects.create(id=51, name='player5', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player6 = Players.objects.create(id=61, name='player6', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player7 = Players.objects.create(id=71, name='player7', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player8 = Players.objects.create(id=81, name='player8', type='Forwarder', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player9 = Players.objects.create(id=91, name='player9', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player10 = Players.objects.create(id=10, name='player10', type='Defender', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player11 = Players.objects.create(id=11, name='player11', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)
			player12 = Players.objects.create(id=12, name='player12', type='Goal Keeper', age=25, noOfMatches=25, goalsScored=25, inEleven=True,belongsTo=team)

			login = self.client.post(reverse('Login-Team'),data = json.dumps(self.team_login2_payload),content_type = 'application/json')
			token = login.data['token'].decode('utf-8')
			headers = {'HTTP_AUTHORIZATION':token}
			eleven_team = self.client.get(
				reverse('Eleven-Team'),
				content_type='application/json',
				**headers
				)

			self.assertEquals(eleven_team.status_code,200)
			self.assertEquals(eleven_team.data["team11s"], [{'noOfMatches': 25, 'goalsScored': 25, 'name': 'player10', 'inEleven': True, 'age': 25, 'id': 10, 'type': 'Defender'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player11', 'inEleven': True, 'age': 25, 'id': 11, 'type': 'Goal Keeper'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player12', 'inEleven': True, 'age': 25, 'id': 12, 'type': 'Goal Keeper'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player2', 'inEleven': True, 'age': 25, 'id': 21, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player3', 'inEleven': True, 'age': 25, 'id': 31, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player4', 'inEleven': True, 'age': 25, 'id': 41, 'type': 'Mid-Fielder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player5', 'inEleven': True, 'age': 25, 'id': 51, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player6', 'inEleven': True, 'age': 25, 'id': 61, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player7', 'inEleven': True, 'age': 25, 'id': 71, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player8', 'inEleven': True, 'age': 25, 'id': 81, 'type': 'Forwarder'}, {'noOfMatches': 25, 'goalsScored': 25, 'name': 'player9', 'inEleven': True, 'age': 25, 'id': 91, 'type': 'Defender'}])

			s = SequenceMatcher(lambda x: x == " ", eleven_team.data['Message'].strip(), "Playing eleven does not meet required condition")
			match = round(s.ratio(), 3)
			self.assertGreaterEqual(match, 0.8)



