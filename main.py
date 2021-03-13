from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        f"Video(name = {name}, views = {views}, likes = {likes})"


# # do this only once to create db then comment it out to avoid db being re-created everytime we run
# db.create_all() 

# request parser
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=int, help="Views of video is required", required=True)
video_put_args.add_argument("likes", type=int, help="Likes on video is required", required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Name of the video ")
video_update_args.add_argument("views", type=int, help="Views of video ")
video_update_args.add_argument("likes", type=int, help="Likes on video ")

# define how object should be serialized
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}


# Resource => class that inherits from Resource
class Video(Resource):
    @marshal_with(resource_fields)
    def get(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="video with given id not found")

        return result

    @marshal_with(resource_fields)
    def put(self, video_id):
        args = video_put_args.parse_args()

        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409, message="video id taken")

        video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_update_args.parse_args()

        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="video with given id not found, cannot update")

        if args["name"]:
            result.name = args["name"]
        if args["views"]:
            result.views = args["views"]
        if args["likes"]:
            result.likes = args["likes"]

        db.session.commit()

        return result, 200

    @marshal_with(resource_fields)
    def delete(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="video with given id not found")

        db.session.delete(result)
        db.session.commit()
        return "", 204


class VideoList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        # result = VideoModel.query.filter(VideoModel.views > 600).all()
        result = VideoModel.query.all()
        return result

# Register the class as a Resource
api.add_resource(Video, "/video/<int:video_id>")
api.add_resource(VideoList, "/videos")

if __name__ == "__main__":
    app.run(debug=True)  # only use debug=true in dev mode not prod
    