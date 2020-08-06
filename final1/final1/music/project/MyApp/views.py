from django.http import HttpResponse
from django.shortcuts import render
from MyApp.models import User,Song,Singer,List
from django.db import connection

song1 = ""
num1 = 0
dict2 = {}
dict3 = {}

def dictfetchall(cursor):
   "Return all rows from a cursor as a dict"
   columns = [col[0] for col in cursor.description]
   return [
       dict(zip(columns, row))
       for row in cursor.fetchall()
   ]

def login(request):
    if request.method == "GET":
        return render(request, 'User/login.html')
    else:
        name = request.POST.get("user_name")
        password = request.POST.get("password")
        # 原始sql语言
        cursor = connection.cursor()
        cursor.execute("SELECT user_name, user_passwd FROM MyApp_user WHERE user_name = %s", [name])
        user_result = cursor.fetchall()
        cursor.close()
        # user_result = User.objects.filter(user_name=user_name)
        context = {}
        if len(user_result) == 1:#
            user_password_ = user_result[0][1]
            if password == user_password_:
                # 新加的
                request.session['is_login'] = True
                request.session['user_name'] = name
                # 设置保持登陆时间，参数0表示cookie将在用户的浏览器关闭时过期
                request.session.set_expiry(0)
                user_results = User.objects.all()
                context["user_results"] = user_results
                return render(request, 'User/choose.html', context=context)
            else:
                context["info"] = "Wrong password！！！"
                context["status"] = 1
                return render(request, 'User/login.html', context=context)
        else:
            context["info"] = "User does not exist！！！"
            context["status"] = 2
            return render(request, 'User/login.html', context=context)

def register(request):
    if request.method == "GET":
        return render(request, 'User/register.html')
    else:
        name = request.POST.get("user_name")
        pswd = request.POST.get("pswd")
        # 原始sql语言
        cursor = connection.cursor()
        cursor.execute("SELECT user_name FROM MyApp_user WHERE user_name = %s", [name])
        user_result = cursor.fetchall()
        # user_result = User.objects.filter(user_name=user_name)
        context = {}
        if len(user_result) == 0:
            cursor.execute("INSERT INTO Myapp_user(user_name, user_passwd) Values(%s, %s)", [name, pswd])
            cursor.close()
            # User.objects.create(user_name=user_name, user_passwd=pswd)
            return render(request, 'User/login.html', context=context)

        else:
            context["info"] = "User name exists！！！"
            context["status"] = 1
            return render(request, 'User/register.html', context=context)


def choose(request):
    return render(request,'User/choose.html')

def mylist(request): #此list里面都是user喜欢的歌
    if request.method == 'GET':
        name = request.session['user_name']
        cursor1 = connection.cursor()
        cursor2 = connection.cursor()
        cursor1.execute("select id from MyApp_user where user_name = %s", [name])
        a = cursor1.fetchall()
        id = a[0]
        # id = User.objects.filter(user_name=user_name).values('id')[0]['id']
        cursor2.execute("select * from MyApp_list where likee = 'like' and user_id = %s", [id])
        results = dictfetchall(cursor2)
        cursor1.close()
        cursor2.close()
        if len(results) == 0:
            return render(request, 'Mylist/mylist.html')
        else:
            context = {'list': results}
            return render(request, 'Mylist/mylist.html', context=context)
    return render(request, 'Mylist/mylist.html')


def search_g(request):
    context = {}
    return render(request, 'Search/search_g.html',context=context)

def allsong(request):
    cursor = connection.cursor()
    cursor.execute("select * from MyApp_song")
    all_song = dictfetchall(cursor)
    context = {
        "all_song": all_song,
    }
    return render(request,'Song/allsong.html',context=context)


#def song(request):
    #song_inform = Song.objects.all()
    #context = {
        #"song_inform": song_inform,
   # }
   # return render(request,'Song/allsong.html',context=context)

def search_song(request):
    global song1,num1,dict2,dict3
    song_name = request.POST.get("song_name")
    cursor = connection.cursor()
    cursor.execute("select * from MyApp_Song where song_name = %s", [song_name])
    d = dictfetchall(cursor)
    if len(d) == 0:
        context = {}
        return render(request, 'Song/allsong.html', context=context)
    else:
        d = d[0]
        #d = Song.objects.filter(song_name=song_name).first()
        info_dic = {}
        info_dic["song name"] = d['song_name']
        song1=d['song_name']
        info_dic["song rate"] = d['rate']
        num1=d['rate']
        #song_inform = Song.objects.all()
        cursor.execute("select * from MyApp_Song")
        song_inform = dictfetchall(cursor)
        context = {
            "result_keys": list(info_dic.keys()),
            "result_values": list(info_dic.values()),
            "song_inform": song_inform,
            "song":song1
        }
        dict2=context
        return render(request,'Song/allsong.html',context=context)

    # global song1,num1,dict2,dict3
    # song_name = request.POST.get("song_name")
    # d = Song.objects.filter(song_name=song_name).first()
    # info_dic = {}
    # info_dic["song name"] = d.song_name
    # song1=d.song_name
    # info_dic["song rate"] = d.rate
    # num1=int(d.rate)
    # song_inform = Song.objects.all()
    # context = {
    #     "result_keys": list(info_dic.keys()),
    #     "result_values": list(info_dic.values()),
    #     "song_inform": song_inform,
    #     "song":song1
    # }
    # dict2=context
    # return render(request,'Song/allsong.html',context=context)



# 这个是修改好的算rate平均值 下面的minus可以删掉了
def add(request):
    global song1, num1
    if request.method == "GET":
        context={
            "song_": song1
        }
        return render(request,'Song/add.html',context=context)
    else:
        num =  int(request.POST.get("number"))
        cursor1 = connection.cursor() #找到song的信息
        cursor2 = connection.cursor() #更新song的信息
        cursor1.execute("select rate_total, rate_num from MyApp_song where song_name = %s", [song1])

        a = dictfetchall(cursor1)
        a = a[0]
        #a = Song.objects.filter(song_name=song1).first()
        if num > 5:
            num = 5
        new_t = a['rate_total'] + num
        new_n = a['rate_num'] + 1
        new_r = "{:.2f}".format(new_t / new_n)
        cursor1.close()
        cursor2.execute("update MyApp_song set rate = %s, rate_num = %s, rate_total = %s where song_name = %s", [new_r, new_n, new_t, song1])
        #Song.objects.filter(song_name=song1).update(rate=new_r)
        #Song.objects.filter(song_name=song1).update(rate_num=new_n)
        #Song.objects.filter(song_name=song1).update(rate_total=new_t)
        context={
            "num":num,
            "song_":song1
        }
        cursor2.close()
        return render(request, 'Song/add.html',context=context )

#def minus(request):
    #global song1, num1
    #if request.method == "GET":
       # context={
         #   "song_": song1
       # }
        #return render(request,'Song/minus.html',context=context)
  #  else:
        #num =  request.POST.get("number")
       # a = Song.objects.filter(song_name=song1).first()
       # num_result= a.rate - int(num)
        #if num_result < 0:
           # num_result = 0
        #Song.objects.filter(song_name=song1).update(rate=num_result)
       #context={
            #"num":num,
           #"song_":song1
     #   }
        #return render(request, 'Song/minus.html',context=context )


def search_by_song_name(request):
    tag = request.POST.get("song_name")
    cursor = connection.cursor()
    tag = '%' + tag + '%'
    cursor.execute("select * from MyApp_song where song_name like %s", [tag])
    results = dictfetchall(cursor)
    #results = Song.objects.filter(song_name__icontains=tag)
    context = {'songs': results}
    cursor.close()
    return render(request, 'Search/search_by_song_name.html', context=context)


def search_by_singer_name(request):
    tag = request.POST.get("singer_name")
    cursor = connection.cursor()
    tag = '%' + tag + '%'
    cursor.execute("select * from MyApp_song where singer_name like %s", [tag])
    results = dictfetchall(cursor)
    context = {'songs': results}
    cursor.close()
    return render(request, 'Search/search_by_song_name.html', context=context)

def advanced_search(request):
    gender = request.POST.get("gender")
    genre = request.POST.get("genre")
    cursor = connection.cursor()
    cursor.execute("select b.* from MyApp_singer a join MyApp_song b on (a.singer_name = b.singer_name) where a.gender = %s and b.genre = %s", [gender, genre])
    results = dictfetchall(cursor)
    context = {'songs': results}
    cursor.close()
    return render(request, 'Search/advanced_search.html', context=context)

#修改好的addsong button的名字要改成like
def addsong(request):
    if request.method == "GET":
        return render(request, 'Song/add_song.html')
    else:
        song = request.POST.get("m_name")
        user = request.session['user_name']
        cursor1 = connection.cursor() #cursor for the song
        cursor2 = connection.cursor() # cursor for the user
        cursor1.execute("select * from MyApp_song where song_name = %s",[song])
        results = dictfetchall(cursor1)
        cursor1.close()
        # results = Song.objects.filter(song_name=song)
        cursor2.execute("select id from MyApp_user where user_name = %s", [user])
        users = cursor2.fetchall()
        id = users[0]
        cursor2.close()
        if len(results) == 0:
            context={}
            context["info"] = "Invalid!!"
            context["status"] = 1
            return render(request, 'Song/add_song.html', context=context)
        else:
            result = results[0]
            cursor3 = connection.cursor() #cursor for the list
            cursor3.execute("select * from MyApp_list where user_id = %s and song_id = %s", [id, result['id']])
            exist = dictfetchall(cursor3)
            if len(exist) == 0:
                cursor3.execute("insert into MyApp_list(user_id, song_id, song_name, singer_name, album, genre, likee) values(%s, %s, %s, %s, %s, %s, 'like')",
                                [id, result['id'], result['song_name'], result['singer_name'], result['album'], result['genre']])
               # List.objects.create(user_id=user_id, song_id=result.id, song_name=result.song_name,
                                    #singer_name=result.singer_name, album=result.album, genre=result.genre, like = 'like')
                cursor3.close()
                return render(request, 'User/choose.html')
            else:
                cursor3.execute("update MyApp_list set likee = %s where user_id = %s and song_id = %s", ['like', id, result['id']])
                #List.objects.filter(user=user_id, song=result.id).update(like = 'like')
                cursor3.close()
                return render(request, 'User/choose.html')
    # if request.method == "GET":
    #     return render(request, 'Song/add_song.html')
    # else:
    #     song = request.POST.get("m_name")
    #     user = request.POST.get("m_num")
    #     user_id = User.objects.filter(user_name=user).values('id')[0]['id']
    #     results = List.objects.filter(song_name=song, user_id = user_id)
    #     if len(results) != 1:
    #         context={}
    #         context["info"] = "Invalid!!"
    #         context["status"] = 1
    #         return render(request, 'Song/add_song.html', context=context)
    #     else:
    #         result = results[0]
    #         List.objects.filter(song_name=song, user_id = user_id).update(like = 'dislike')
    #         context = {}
    #         return render(request, 'Song/add_song.html', context=context)



# 修改好的delete button名字改成dislike
def deletesong(request):
    if request.method == "GET":
        return render(request, 'Song/delete_song.html')
    else:
        song = request.POST.get("m_name")
        user = request.session['user_name']
        cursor1 = connection.cursor()  # cursor for the song
        cursor2 = connection.cursor()  # cursor for the user
        cursor1.execute("select * from MyApp_song where song_name = %s", [song])
        results = dictfetchall(cursor1)
        cursor1.close()
        # results = Song.objects.filter(song_name=song)
        cursor2.execute("select id from MyApp_user where user_name = %s", [user])
        users = cursor2.fetchall()
        id = users[0]
        cursor2.close()
        if len(results) == 0:
            context={}
            context["info"] = "Invalid!!"
            context["status"] = 1
            return render(request, 'Song/delete_song.html', context=context)
        else:
            result = results[0]
            cursor3 = connection.cursor()  # cursor for the list
            cursor3.execute("select * from MyApp_list where user_id = %s and song_id = %s", [id, result['id']])
            exist = dictfetchall(cursor3)
            if len(exist) == 0:
                cursor3.execute("insert into MyApp_list(user_id, song_id, song_name, singer_name, album, genre, likee) values(%s, %s, %s, %s, %s, %s, 'dislike')",
                                [id, result['id'], result['song_name'], result['singer_name'], result['album'], result['genre']])
               # List.objects.create(user_id=user_id, song_id=result.id, song_name=result.song_name,
                                    #singer_name=result.singer_name, album=result.album, genre=result.genre, like = 'dislike')
                cursor3.close()
                return render(request, 'User/choose.html')
            else:
                 cursor3.execute("update MyApp_list set likee = %s where user_id = %s and song_id = %s", ['dislike', id, result['id']])
                  # List.objects.filter(user=user_id, song=result.id).update(like = 'dislike')
                 cursor3.close()
                 return render(request, 'User/choose.html')


'''
def like(request):
    if request.
'''


def MyRecommend(request):
    if request.method == "GET":
        return render(request, 'Mylist/MyRecommend.html')


def exit(request):
    return render(request,'User/login.html')

