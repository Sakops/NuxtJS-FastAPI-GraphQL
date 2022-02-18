from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from pydantic.dataclasses import dataclass
import strawberry
from strawberry.fastapi import GraphQLRouter
from pony.orm import Database, PrimaryKey, Required, db_session

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = Database(provider='sqlite', filename='database.db', create_db=True)


class PostModel(db.Entity):
    _table_ = "Posts"
    id = PrimaryKey(int, auto=True)
    post = Required(str)
    content = Required(str)


db.generate_mapping(create_tables=True)


@dataclass
class PostDTO:
    post: str
    content: str


@strawberry.type(name="Post")
class PostType:
    id: int
    post: str
    content: str


@strawberry.input
class PostInput:
    post: str
    content: str


@strawberry.type
class Query:

    @strawberry.field
    def getPosts(self) -> List[PostType]:  # TODO: nullable type User
        with db_session:
            posts = PostModel.select()
            result = [PostType(**p.to_dict()) for p in posts]
        return result

    @strawberry.field
    def getPost(self, id: int) -> PostType:
        with db_session:
            post = PostModel[id]
            result = PostType(**post.to_dict())
        return result


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_post(self, postInput: PostInput) -> PostType:
        PostDTO(**postInput.__dict__)
        with db_session:
            user = PostModel(**postInput.__dict__)
            db.commit()
            result = PostType(**user.to_dict())
        return result

    @strawberry.mutation
    def update_post(self, id: int, postInput: PostInput) -> PostType:
        PostDTO(**postInput.__dict__)
        with db_session:
            post = PostModel[id]
            post.post = postInput.post
            post.content = postInput.content
            db.commit()
            result = PostType(**post.to_dict())
        return result

    @strawberry.mutation
    def delete_post(self, id: int) -> PostType:
        with db_session:
            db.commit()
            if PostModel.exists(id=id):
                post = PostModel[id]
                result = PostType(**post.to_dict())
                post.delete()
            else:
                raise HTTPException(
                    status_code=404, detail=f"User with id of {id} not found")
            db.commit()
        return result


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
