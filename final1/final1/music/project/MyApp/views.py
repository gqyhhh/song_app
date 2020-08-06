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


def generate_recommendations(user_id):
    cursor = musicdb.cursor()
    input = (user_id, user_id)
    sql = "SELECT user.Username, COUNT(album) FROM MyApp_list l, user u WHERE l.Username = %s AND album IN (SELECT album FROM MyApp_list WHERE MyApp_list.Username = u.Username AND MyApp_list.Username <> %s) GROUP BY u.Username ORDER BY COUNT(album) DESC LIMIT 10;"
    cursor.execute(sql,input)
    result_pool = cursor.fetchall()
    if len(result_pool) == 0:
        top_album = get_top_album(user_id)
        sql = "SELECT DISTINCT SongId FROM Songs WHERE album = %s AND SongId NOT IN (SELECT SongId FROM Likes WHERE Username = %s) LIMIT 10"
        val = (top_album,user_id)
        cursor.execute(sql,val)
        result = cursor.fetchall()
        if len(result) == 0:
            random_song_sql = "SELECT SongId FROM Songs ORDER BY rate LIMIT 10"
            cursor.execute(random_song_sql)
            result = cursor.fetchall()
        session['recs'] = result
        return
    scores = {}
    for user in result:
        scores[user[0]] = generate_recommendation_score(user_id, )
    best = get_result(scores)
    cursor.close()
    session['list'] = best

def generate_recommendation_score(current_user,song_id):
    if get_top_album(current_user) == get_album(song_id):
        score += 60
    if get_top_singer(current_user) == get_singer(song_id):
        score += 30
    if  get_top_genre(current_user) == get_genre(song_id):
        score += 10
    return score

def get_result(scores):
    count = Counter(scores)
    return count.most_common(10)

def get_top_album(user):
    cursor = musicdb.cursor()
    sql = "SELECT album, COUNT(album) FROM (SELECT SongId FROM MyApp_list l WHERE Username = %s) temp JOIN Songs ON temp.SongId = Songs.SongId GROUP BY album ORDER BY COUNT(album) DESC LIMIT 1"
    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0]

def get_top_singer(user):
    cursor = musicdb.cursor()
    sql = "SELECT singer_name, COUNT(singer_name) FROM (SELECT SongId FROM MyApp_list l WHERE Username = %s) temp JOIN Songs ON temp.SongId = Songs.SongId GROUP BY singer_name ORDER BY COUNT(singer_name) DESC LIMIT 1"

    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0]


def get_top_genre(user):
    cursor = musicdb.cursor()
    sql = "SELECT genre, COUNT(genre) FROM (SELECT SongId FROM MyApp_list l WHERE Username = %s) temp JOIN Songs ON temp.SongId = Songs.SongId GROUP BY genre ORDER BY COUNT(genre) DESC LIMIT 1"

    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0]

def get_genre(song):
    cursor = musicdb.cursor()
    sql = "SELECT genre from Songs WHERE (SongId = song.SongId)GROUP BY genre"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]
def get_album(song):
    cursor = musicdb.cursor()
    sql = "SELECT album from Songs WHERE (SongId = song.SongId)GROUP BY album"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]
def get_singer(song):
    cursor = musicdb.cursor()
    sql = "SELECT singer_name from Songs WHERE (SongId = song.SongId)GROUP BY singer_name"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# def MyRecommend(request):
#     if request.method == "GET":
#         user_name = request.session['user_name']
#         user_id = User.objects.filter(user_name=user_name).values('id')[0]['id']
#         pool= List.objects.filter(user = user_id )
#         if len(pool) == 0:
#             results = Song.objects.order_by('-rate')[:10]
#             context = {'list': results}
#             return render(request, 'Mylist/MyRecommend.html', context=context)
#         else:
#             id = User.objects.filter(user_name=user_name).values('id')[0]['id']
#             genre_pool =  List.objects.filter(user=id).annotate(genre_count=Count('genre')).order_by('-genre_count')[:2]
#             album_pool = List.objects.filter(user=id).annotate(album_count=Count('album')).order_by('-album_count')[:2]
#             singer_pool = List.objects.filter(user=id).annotate(singer_count=Count('singer_name')).order_by('-singer_count')[:2]
#             genre_first = genre_pool[0].genre
#             genre_second = genre_pool[0].genre
#             if len(genre_pool) > 1:
#                 genre_second = genre_pool[1].genre
#             else:
#                 genre_second = genre_pool[0].genre
#             album_first = album_pool[0].album
#             album_second = album_pool[0].album
#             if len(album_pool) > 1:
#                 album_second = album_pool[1].album
#             else:
#                 album_second = album_pool[0].album
#             singer_first = singer_pool[0].singer_name
#             singer_second = singer_pool[0].singer_name
#             if len(singer_pool) > 1:
#                 singer_second = singer_pool[1].singer_name
#             else:
#                 singer_second = singer_pool[0].singer_name
#
#             candidate_genre_1 = Song.objects.filter(genre = genre_first)
#             candidate_genre_2 = Song.objects.filter(genre = genre_second)
#             candidate_album_1 = Song.objects.filter(album = album_first)
#             candidate_album_2 = Song.objects.filter(album = album_second)
#             candidate_singer_1 = Song.objects.filter(singer_name = singer_first)
#             candidate_singer_2 = Song.objects.filter(singer_name = singer_second)
#             results_pool = (candidate_album_2|candidate_album_1)
#             result = ( candidate_singer_2 | candidate_singer_1 | candidate_genre_2| candidate_genre_1)
#             if len(results_pool) > 0:
#                 result = results_pool
#             results = result.order_by("song_name")
#
#             context = {'list': results}
#             return render(request, 'Mylist/MyRecommend.html', context=context)
#     return render(request, 'Mylist/MyRecommend.html', context=context)
def exit(request):
    return render(request,'User/login.html')

