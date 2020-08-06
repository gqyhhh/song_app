from django.db import models

class User(models.Model):
    user_name = models.CharField(max_length=50)
    user_passwd = models.CharField(max_length=50)

class Singer(models.Model):
    singer_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    #albums = models.CharField(max_length=50) #list of albums of the singer
    #songs = models.CharField(max_length=50) #list of songs of the singer

#加了rate_total和rate_num
class Song(models.Model):
    song_name = models.CharField(max_length=50)
    singer_name = models.CharField(max_length=50)
    album = models.CharField(max_length=50)
    release_date = models.CharField(max_length=50)
    genre = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=3, decimal_places=2) #rate取到小数点后两位
    rate_total = models.DecimalField(max_digits=100000, decimal_places=2)
    rate_num = models.IntegerField()

# 加了like的attribute 把下面的like table去掉了
class List(models.Model): #it is a sub-class of song
    user = models.ForeignKey('User', on_delete = models.CASCADE)
    song = models.ForeignKey('Song', on_delete = models.CASCADE)
    song_name = models.CharField(max_length=50)
    singer_name = models.CharField(max_length=50)
    album = models.CharField(max_length=50)
    genre = models.CharField(max_length=50)
    likee = models.CharField(max_length=50)
