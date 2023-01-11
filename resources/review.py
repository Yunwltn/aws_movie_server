from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class ReviewListResource(Resource) :

    @jwt_required()
    def post(self) :
        # {"movie_id": "50",
        # "rating": "1" }
    
        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into rating
                    (user_id, movie_id, rating)
                    values
                    (%s, %s, %s);'''

            record = ( user_id, data['movie_id'], data['rating'])

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200

    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select m.title, r.rating, r.movie_id
                    from rating r
                    join movie m
                    on r.movie_id = m.id
                    where user_id = %s'''

            record = ( user_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200

class MovieReviewResource(Resource) :
    def get(self, movie_id) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select r.id, u.name, u.gender, r.rating
                    from rating r
                    join user u
                    on r.user_id = u.id
                    where r.movie_id = %s
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            record = ( movie_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200
