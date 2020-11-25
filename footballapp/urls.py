from django.contrib import admin
from django.urls import path, include
from .views import registerAdmin, loginAdmin, deleteTeamByAdmin, deletePlayersByAdmin, getTeamsAdmin, updateTeamByAdmin, elevenTeamByAdmin
from .views import playersViewByAdmin, playersUpdateByAdmin, playersRegisterByAdmin, playersDeleteByAdmin
from .views import registerTeam, loginTeam, updateTeam, deleteTeam, getTeam, elevenTeam
from .views import registerPlayer,updatePlayer, viewPlayers, deletePlayers, deleteAllPlayers
from .views import viewMappings, updateMappingsByAdmin

urlpatterns = [
	path('register/', registerAdmin, name='Register-Admin'),
	path('login', loginAdmin, name='Login-Admin'),
	
	path('admin/teams/delete/<int:id>',deleteTeamByAdmin, name='Delete-Team-Admin'),
	path('admin/teams/view',getTeamsAdmin, name='View-Team-Admin'),
	path('admin/teams/update/<int:id>',updateTeamByAdmin, name='Update-Team-Admin'),
	path('admin/teams/eleven/<int:id>',elevenTeamByAdmin, name='Eleven-Team-Admin'),

	path('admin/players/view/<int:id>',playersViewByAdmin, name='View-Players-Admin'),
	path('admin/players/delete/<int:id>',deletePlayersByAdmin, name='Delete-Players-Admin'),
	path('admin/players/update/<int:id>',playersUpdateByAdmin, name='Update-Players-Admin'),
	path('admin/players/register/<int:id>',playersRegisterByAdmin, name='Register-Players-Admin'),
	path('admin/players/deleteAll/<int:id>',playersDeleteByAdmin, name='Delete-All-Players-Admin'),


	path('teams/registration', registerTeam, name='Register-Team'),	
	path('teams/login', loginTeam, name='Login-Team'),	
	path('teams/view', getTeam, name ='View-Team'), 

	path('teams/update', updateTeam, name='Update-Team'),
	path('teams/delete', deleteTeam, name ='Delete-Team'),
	path('teams/eleven', elevenTeam, name ='Eleven-Team'), 
	
	path('players/register', registerPlayer, name='Register-Player'),
	path('players/update/<int:id>', updatePlayer , name='Update-player'),
	path('players/view', viewPlayers, name='View-Player'),
	path('players/delete/<int:id>', deletePlayers, name='Delete-Player'),
	path('players/deleteAll', deleteAllPlayers, name='Delete-All-Players'),

	path('mapping/view', viewMappings, name='View-Mappings'),
	path('mapping/update/<int:id>', updateMappingsByAdmin, name='Update-Mappings'),


]