from django.shortcuts import render
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

# Create your views here.

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view

from ..models import AdminProfile, Team, Players, Mappings

import jwt
import datetime
from functools import wraps

#WORKING
@api_view(['POST'])
def registerTeam(request):
	team = request.data
	if team:
		hash_password = make_password(team['password'])
		try:
			new_team = Team(name=team['name'], password=hash_password, country = team['country'], coach=team['coach'])
			new_team.save()
			data = {}
			data['name'] = team['name']
			data['country'] = team['country']
			data['coach'] = team['coach']

			resp = data
			return Response(data=resp, status=status.HTTP_200_OK)
		except:
			resp = {"Message":"Registration Failed"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	

	else:
		resp = {"Message":"Registration Failed"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['POST'])
def loginTeam(request):
	details = request.data
	name = details['name']
	password = details['password']
	teamobj = Team.objects.filter(name=name).all()

	if teamobj:
		data = {}
		data['country'] = teamobj[0].country
		data['coach'] = teamobj[0].coach
		data['name'] = teamobj[0].name

		try:
			check = check_password(password, teamobj[0].password)
			if check:
				token = jwt.encode({'id':teamobj[0].id, 'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=30)}, settings.SECRET_KEY)
				resp = {"team":data, "token":token}
				return Response(data=resp, status=status.HTTP_200_OK)
			else:
				resp = {"Message":"Could not verify"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		except:
			resp = {"Message":"Could not verify"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Could not verify"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def updateTeam(request):
	details = request.data
	token = request.META.get('HTTP_AUTHORIZATION')
	fields = ['name','country','coach']
	if token:
		try:
			data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
			current_user = Team.objects.filter(id=data['id']).get()

			if "name" in details.keys():
				current_user.name = details['name']
			if 'country' in details.keys():
				current_user.country = details['country']
			if 'coach' in details.keys():
				current_user.coach = details['coach']

			# current_user.name = details['name']
			current_user.save()
			resp = {"Message":"Update successful"}
			return Response(data=resp, status=status.HTTP_200_OK)
		except Exception as e:
			raise e
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['DELETE'])
def deleteTeam(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
		current_user = Team.objects.filter(id=data['id']).all()
		if len(current_user)==1:
			try:
				current_user.delete()
				return Response(data={}, status=status.HTTP_204_NO_CONTENT)		
			except Exception as e:
				raise e
		else:
			resp = {"Message":"Couldn't Delete"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['GET'])
def getTeam(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
		current_user = Team.objects.all()
		output = []
		for a in current_user:
			data = {}
			data['id'] = a.id
			data['name'] = a.name
			data['country'] = a.country
			data['coach'] = a.coach
			output.append(data)
		# data.append(current_user.id)
		return Response(data=output, status=status.HTTP_200_OK)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['GET'])
def elevenTeam(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
		goalkeeper = Players.objects.filter(inEleven=True, belongsTo=data['id'], type='Goal Keeper').all()
		forward = Players.objects.filter(inEleven=True, belongsTo=data['id'], type='Forwarder').all()
		mid_field = Players.objects.filter(inEleven=True, belongsTo=data['id'], type='Mid-Fielder').all()
		defender = Players.objects.filter(inEleven=True, belongsTo=data['id'], type='Defender').all()
		try:
			ineleven = Players.objects.filter(belongsTo=data['id'], inEleven=True).all()
			output = []
			for a in ineleven:
				data = {}
				data['id'] = a.id
				data['name'] = a.name
				data['age'] = a.age
				data['type'] = a.type
				data['inEleven'] = a.inEleven
				data['goalsScored'] = a.goalsScored
				data['noOfMatches'] = a.noOfMatches
				output.append(data)
			if len(goalkeeper)==1 and len(forward)>=1 and len(mid_field)>=1 and len(defender)>=1 and len(ineleven)==11:	
				resp = {"Message":"", "team11s":output}	
			else:
				resp = {"Message":"Playing eleven does not meet required condition", "team11s":output}		
			return Response(data=resp, status=status.HTTP_200_OK)
		except Exception as e:
			raise e

	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#########################################################################################################

#WORKING
@api_view(['POST'])
def registerPlayer(request):
	details = request.data
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
		current_user = Team.objects.filter(id=data['id'])

		try:
			new_player = Players(name=details['name'], inEleven=False, age=details['age'],noOfMatches= details['noOfMatches'], goalsScored=details['goalsScored'], type =details['type'], belongsTo=current_user[0])
			new_player.save()
			resp = {"Message":"Registration Success"}
			return Response(data=resp, status=status.HTTP_200_OK)
		except:
			resp = {"Message":"Could not register"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def updatePlayer(request, id):
	details = request.data
	token = request.META.get('HTTP_AUTHORIZATION')
	fields = ['name','age','noOfMatches','goalsScored','type']
	if token:
		try:

			data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
			current_user = Players.objects.filter(id=int(id)).get()

			if "name" in details.keys():
				current_user.name = details['name']
			if "age" in details.keys():
				current_user.age = details['age']
			if "inEleven" in details.keys():
				current_user.inEleven = details['inEleven']
			if "noOfMatches" in details.keys():
				current_user.noOfMatches = details['noOfMatches']
			if "goalsScored" in details.keys():
				current_user.goalsScored = details['goalsScored']
			if "type" in details.keys():
				current_user.type = details['type']

			current_user.save()
			resp = {"Message":"Update successful"}
			return Response(data= resp, status=status.HTTP_200_OK)
		except Exception as e:
			raise e
	else:
		resp = {'Message':'Token required'}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(["GET"])
def viewPlayers(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		try:
			data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
			players = Players.objects.filter(belongsTo=data['id']).all()
			output = []
			for a in players:
				data = { }
				data['id']=a.id
				data['name']=a.name
				data['age'] = a.age
				data['inEleven'] = a.inEleven
				data['type'] = a.type
				data['noOfMatches'] = a.noOfMatches
				data['goalsScored'] = a.goalsScored
				output.append(data)
			return Response(data=output, status=status.HTTP_200_OK)
		except Exception as e:
			raise e
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deletePlayers(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		try:
			data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
			players = Players.objects.filter(belongsTo=data['id'], id=id).get()
			players.delete()
			return Response(data={}, status=status.HTTP_204_NO_CONTENT)			
		except:
			resp = {"Message":"Couldn't delete"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['DELETE'])
def deleteAllPlayers(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		try:
			data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
			players = Players.objects.filter(belongsTo=data['id']).all()
			if players:
				for a in players:
					a.delete()
				return Response(data={}, status=status.HTTP_204_NO_CONTENT)			
			else:
				resp = {"Message":"couldn't delete"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

		except:
			resp = {"Message":"couldn't delete"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)


################################################################################################################

#WORKING
@api_view(['POST'])
def registerAdmin(request):
	admin = request.data
	# print(admin['name'])
	# print(admin['password'])
	if admin['name'] and admin['password']:
		hash_password = make_password(admin['password'])
		new_admin = AdminProfile(name=admin['name'], password=hash_password)
		new_admin.save()
		resp = {"Message":"Registration Success"}
		return Response(data=resp, status=status.HTTP_200_OK)

	else:
		resp = {"Message":"Registration Failed"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#WORKING
@api_view(['POST'])
def loginAdmin(request):
	details = request.data
	name = details['name']
	password = details['password']
	adminobj = AdminProfile.objects.filter(name=name).all()

	if adminobj:
		try:
			check = check_password(password, adminobj[0].password)
			if check:
				token = jwt.encode({'id':adminobj[0].id, 'name':adminobj[0].name, 'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=30)}, settings.SECRET_KEY)
				data ={}
				data['id']=adminobj[0].id
				data['name'] = adminobj[0].name
				resp = {"token":token, "admin":data}
				return Response(data=resp, status=status.HTTP_200_OK)
			else:
				resp = {"Message":"Could not verify"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		except:
			resp = {"Message":"Could not verify"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Could not verify"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def deleteTeamByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		try:
			data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
			team = Team.objects.filter(id=id).all()
			if team:
				for a in team:
					a.delete()
				return Response(data={}, status=status.HTTP_204_NO_CONTENT)
			else:
				resp = {"Message":"couldn't delete"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

		except:
			resp = {"Message":"couldn't delete"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deletePlayersByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		try:
			data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
			players = Players.objects.filter(id=id).all()
			if players:
				for a in players:
					a.delete()
				return Response(data={}, status=status.HTTP_204_NO_CONTENT)			
			else:
				resp = {"Message":"couldn't delete"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

		except:
			resp = {"Message":"couldn't delete"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

#################################################################################33333

#WORKING
@api_view(['GET'])
def getTeamsAdmin(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
		if len(data) == 3:
			try:
				team = Team.objects.all()
				output = []
				for a in team:
					data = {}
					data['id'] = a.id
					data['name'] = a.name
					data['country'] = a.country
					data['coach'] = a.coach
					output.append(data)
				return Response(data=output, status=status.HTTP_200_OK)
			except:
				resp = {"Message":"unable to fetch"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def updateTeamByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data) == 3:
			try:
				details = request.data
				current_user = Team.objects.filter(id=id).get()
				if "name" in details.keys():
					current_user.name = details['name']
				if "country" in details.keys():
					current_user.country = details['country']
				if "coach" in details.keys():
					current_user.coach = details['coach']
				current_user.save()

				data = {}
				data['id'] = current_user.id
				data['name'] =  current_user.name
				data['coach'] = current_user.coach
				data['country'] = current_user.country

				return Response(data=data, status=status.HTTP_200_OK)
			except Exception as e:
				raise e

				# resp = {"Message":"unable to update "}
				# return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def elevenTeamByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		goalkeeper = Players.objects.filter(inEleven=True, belongsTo=id, type='Goal Keeper').all()
		forward = Players.objects.filter(inEleven=True, belongsTo=id, type='Forwarder').all()
		mid_field = Players.objects.filter(inEleven=True, belongsTo=id, type='Mid-Fielder').all()
		defender = Players.objects.filter(inEleven=True, belongsTo=id, type='Defender').all()
		if len(data) == 3:
			ineleven = Players.objects.filter(belongsTo=id, inEleven=True).all()
			output = []
			for a in ineleven:
				data = {}
				data['id'] = a.id
				data['name'] = a.name
				data['age'] = a.age
				data['type'] = a.type
				data['inEleven'] = a.inEleven
				data['goalsScored'] = a.goalsScored
				data['noOfMatches'] = a.noOfMatches
				output.append(data)
			if len(goalkeeper)==1 and len(forward)>=1 and len(mid_field)>=1 and len(defender)>=1 and len(ineleven)==11:	
				resp = {"Message":"", "team11s":output}	
			else:
				resp = {"Message":"Playing eleven does not meet required condition", "team11s":output}		
			return Response(data=resp, status=status.HTTP_200_OK)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def playersViewByAdmin(request,id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data) == 3:
			try:
				players = Players.objects.filter(belongsTo=id).all()
				output = []
				for a in players:
					data = { }
					data['id']=a.id
					data['name']=a.name
					data['age'] = a.age
					data['inEleven'] = a.inEleven
					data['type'] = a.type
					data['noOfMatches'] = a.noOfMatches
					data['goalsScored'] = a.goalsScored
					output.append(data)
				return Response(data=output, status=status.HTTP_200_OK)
				'''
				players = Players.objects.filter(id=id).get()
				test = {}
				test["name"] = players.name
				test["age"] = players.age
				test["goalsScored"] = players.goalsScored
				test["type"] = players.type
				test["noOfMatches"] = players.noOfMatches
				return Response(data=test, status=status.HTTP_200_OK)			
				'''
			except:
				resp = {"Message":"not a valid id"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	

@api_view(['POST'])
def playersUpdateByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data)==3:
			try:
				details = request.data
				players = Players.objects.filter(id=id).get()
				if "name" in details.keys():
					players.name = details['name']
				if "noOfMatches" in details.keys():
					players.noOfMatches = details['noOfMatches']
				if "inEleven" in details.keys():
					players.inEleven = details['inEleven']	
				if "goalsScored" in details.keys():
					players.goalsScored = details['goalsScored']
				if "type" in details.keys():
					players.type = details['type']
				if "age" in details.keys():
					players.age = details['age']
				players.save()

				test = {"Message":"Update successful"}
				return Response(data=test, status=status.HTTP_200_OK)			
			except:
				resp = {"Message":"Not a valid id"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	

@api_view(['POST'])
def playersRegisterByAdmin(request,id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data) == 3:
			try:
				details = request.data
				team = Team.objects.filter(id=id).get()
				new_player = Players(name=details['name'], age=details['age'],noOfMatches= details['noOfMatches'], goalsScored=details['goalsScored'], type =details['type'], belongsTo=team)
				new_player.save()
				data = {}
				data['name'] = details['name']
				data['age'] = details['age']
				data['noOfMatches'] = details['noOfMatches']
				data['goalsScored'] = details['goalsScored']
				data['type'] = details['type']
				data['belongsTo'] = id
				
				return Response(data=data, status=status.HTTP_200_OK)			
			except:
				resp = {"id":id,"Message":"not a valid id"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	


@api_view(['DELETE'])
def playersDeleteByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data)==3:
			try:
				team_players = Players.objects.filter(belongsTo=id).all()
				for a in team_players:
					a.delete()
				return Response(data={}, status=status.HTTP_204_NO_CONTENT)			
			except:
				resp = {"Message":"Could not delete"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	


#WORKING
@api_view(['GET'])
def viewMappings(request):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		mappings = Mappings.objects.all()
		output = []
		for a in mappings:
			data = {}
			data['id'] = a.id
			data['name'] = a.name
			data['category'] = a.category
			output.append(data)
		return Response(data=output, status=status.HTTP_200_OK)
			
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	


@api_view(['PATCH'])
def updateMappingsByAdmin(request, id):
	token = request.META.get('HTTP_AUTHORIZATION')
	if token:
		data = jwt.decode(token,settings.SECRET_KEY, algorithms='HS256')
		if len(data) == 3:
			details = request.data
			try:
				mapping = Mappings.objects.filter(id=id).get()
				mapping.name = details['name']
				mapping.save()
				resp = {"Message":"Update successful"}
				return Response(data=resp, status=status.HTTP_200_OK)
			except:
				resp = {"Message":"Cannot update"}
				return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)

			return Response(data=output, status=status.HTTP_200_OK)
		else:
			resp = {"Message":"Not an admin"}
			return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)
	else:
		resp = {"Message":"Token required"}
		return Response(data=resp, status=status.HTTP_400_BAD_REQUEST)	

	



