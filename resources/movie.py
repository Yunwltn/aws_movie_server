from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class MovieListResource(Resource) :

    @jwt_required(optional=True) # 비회원도 동작 가능하게 설정
    def get(self) :
        order = request.args.get('order')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()
        # 토큰이 없을때는 None값이 저장된다

        try :
            connection = get_connection()

            if user_id is None :
                query = '''select m.id, m.title, ifnull(count(r.movie_id),0) as cnt,
                        ifnull(avg(r.rating),0) as avg
                        from movie m
                        left join rating r
                        on m.id = r.movie_id
                        group by m.id
                        order by ''' + order + ''' desc
                        limit ''' + offset + ''' , ''' + limit + ''' ; '''

                cursor = connection.cursor(dictionary= True)

                cursor.execute(query, )

            else :
                query = '''select m.id, m.title, ifnull(count(r.movie_id),0) as cnt,
                        ifnull(avg(r.rating),0) as avg, 
                        if(f.user_id is null, 0, 1) as 'favorite'
                        from movie m
                        left join rating r on m.id = r.movie_id
                        left join favorite f on f.movie_id= m.id and f.user_id= %s
                        group by m.id
                        order by ''' + order + ''' desc
                        limit ''' + offset + ''' , ''' + limit + ''' ; '''

                record = (user_id, )

                cursor = connection.cursor(dictionary= True)

                cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['avg'] = float(row['avg'])
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200

class MovieSearchResource(Resource) :

    def get(self) :
        keyword = request.args.get('keyword')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select m.id, m.title, ifnull(count(r.movie_id),0) as cnt,
                    ifnull(round(avg(r.rating),1),0) as avg
                    from movie m
                    left join rating r
                    on m.id = r.movie_id
                    where m.title like '%''' + keyword + '''%'
                    group by m.id
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['avg'] = float(row['avg'])
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200

class MovieInformationResource(Resource) :

    @jwt_required(optional=True)
    def get(self, movie_id) :
        try :
            connection = get_connection()

            query = '''select m.id, m.title, m.year, m.attendance,
                    ifnull(avg(r.rating),0) as avg, ifnull(count(r.movie_id),0) as cnt
                    from movie m
                    left join rating r
                    on m.id = r.movie_id
                    where m.id = %s;'''

            record = (movie_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            # 세이프코딩
            if result_list[0]["id"] is None :
                return {"error" : "잘못된 영화 아이디입니다"}, 400

            i = 0
            for row in result_list :
                result_list[i]['year'] = row['year'].isoformat()
                result_list[i]['avg'] = float(row['avg'])
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "movie" : result_list[0]}, 200
