import json
import uuid
from enum import Enum, IntEnum
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound

from .db import engine
ROOM_MAX_USER_COUNT = 4


class InvalidToken(Exception):
    """指定されたtokenが不正だったときに投げる"""


class SafeUser(BaseModel):
    """token を含まないUser"""

    id: int
    name: str
    leader_card_id: int

    class Config:
        orm_mode = True


class RoomInfo(BaseModel):
    room_id: int
    live_id: int
    joined_user_count: int
    max_user_count: int

    class Config:
        orm_mode = True


def create_user(name: str, leader_card_id: int) -> str:
    """Create new user and returns their token"""
    token = str(uuid.uuid4())
    # NOTE: tokenが衝突したらリトライする必要がある.
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `user` (name, token, leader_card_id) VALUES (:name, :token, :leader_card_id)"
            ),
            {"name": name, "token": token, "leader_card_id": leader_card_id},
        )
        # print(result)
    return token


def _get_user_by_token(conn, token: str) -> Optional[SafeUser]:
    # TODO: 実装
    result = conn.execute(
        text("SELECT `id`, `name`, `leader_card_id` FROM `user` WHERE `token`=:token"),
        dict(token=token),
    )
    try:
        row = result.one()
    except NoResultFound:
        return None
    return SafeUser.from_orm(row)


def get_user_by_token(token: str) -> Optional[SafeUser]:
    with engine.begin() as conn:
        return _get_user_by_token(conn, token)


def update_user(token: str, name: str, leader_card_id: int) -> None:
    # このコードを実装してもらう
    with engine.begin() as conn:
        # TODO: 実装
        _ = conn.execute(
            text(
                "UPDATE `user` SET name=:name, leader_card_id=:leader_card_id\
                WHERE token=:token"
            ),
            {"name": name, "token": token, "leader_card_id": leader_card_id},
        )


def _join_room(conn, room_id: int, user_id: int) -> None:
    _ = conn.execute(
        text(
            "INSERT INTO `room_member` (`room_id`, `user_id`)\
            VALUES (:room_id, :user_id)"
        ),
        {"room_id": room_id, "user_id": user_id},
    )


def create_room(live_id: int, difficulty: int, token: str) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `room` (`live_id`, `joined_user_count`, `max_user_count`)\
                VALUES (:live_id, :joined_user_count, :max_user_count)"
            ),
            {"live_id": live_id, "joined_user_count": 1, "max_user_count": ROOM_MAX_USER_COUNT},
        )
        room_id = result.lastrowid
        user = _get_user_by_token(conn, token)
        _join_room(conn, room_id, user.id)
        # result = conn.execute(
        #     text(
        #         "INSERT INTO `room_member` (`room_id`, `user_id`)\
        #         VALUES (:room_id, :user_id)"
        #     ),
        #     {"room_id": room_id, "user_id": user.id},
        # )

    return room_id


def list_room(live_id: int) -> List[RoomInfo]:
    with engine.begin() as conn:
        if live_id == 0:
            result = conn.execute(
                text("SELECT `room_id`, `live_id`, `joined_user_count`,\
                    `max_user_count` FROM `room`")
            )
        else:
            result = conn.execute(
                text("SELECT `room_id`, `live_id`, `joined_user_count`,\
                    `max_user_count` FROM `room` WHERE live_id=:live_id"),
                {"live_id": live_id},
            )
        return [RoomInfo.from_orm(row) for row in result]


def join_room(room_id: int, difficulty: int) -> RoomInfo:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "SELECT `room_id`, `live_id`, `joined_user_count`, `max_user_count`\
                FROM `room` WHERE room_id=:room_id",
            ),
            {"room_id": room_id},
        )
        try:
            row = result.one()
        except NoResultFound:
            return None
    room_info = RoomInfo.from_orm(row)
    print(room_info)
    return room_info


def judge_join(room_info: RoomInfo, token: str) -> str:
    if room_info is None:
        return "Disbanded"
    elif room_info.joined_user_count == room_info.max_user_count:
        return "RoomFull"
    elif room_info.joined_user_count < room_info.max_user_count:

        return "Ok"
    else:
        return "OtherError"

