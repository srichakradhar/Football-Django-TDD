from django.db import models

# Create your models here.
class AdminProfile(models.Model):
	name = models.CharField(max_length=40, null=False, unique=True)
	password = models.CharField(max_length=150, null=False)

class Players(models.Model):
	name = models.CharField(max_length=40, null=False)
	age = models.IntegerField(null=False)
	noOfMatches = models.IntegerField(null=False)
	goalsScored = models.IntegerField(null=False)
	type = models.CharField(max_length=40, null=False)
	belongsTo = models.ForeignKey("Team", on_delete=models.CASCADE)
	inEleven  = models.BooleanField(default=False)
	
class Team(models.Model):
	name = models.CharField(max_length=40, null=False, unique=True)
	password = models.CharField(max_length=150, null=False)
	country = models.CharField(unique=True, max_length=10)
	coach = models.CharField(max_length=50, null=False)

class Mappings(models.Model):
	name = models.CharField(max_length=50, null=True)
	category = models.CharField(max_length=100, null=False)

class Viewer(models.Model):
	name = models.CharField(max_length=40, null=False, unique=True)
	password = models.CharField(max_length=150, null=False)

class Bookings(models.Model):
	matchId = models.IntegerField(null=False)
	bookingMadeBy = models.ForeignKey("Viewer", on_delete=models.CASCADE)
	
	

