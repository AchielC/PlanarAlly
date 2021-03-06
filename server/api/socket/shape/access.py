from typing import Any, Dict

import auth
from api.socket.initiative import send_client_initiatives
from app import app, logger, sio
from models import Floor, Layer, Location, PlayerRoom, Room, Shape, ShapeOwner, User
from models.shape.access import has_ownership
from state.game import game_state


@sio.on("Shape.Owner.Add", namespace="/planarally")
@auth.login_required(app, sio)
async def add_shape_owner(sid: int, data: Dict[str, Any]):
    pr: PlayerRoom = game_state.get(sid)

    try:
        shape = Shape.get(uuid=data["shape"])
    except Shape.DoesNotExist as exc:
        logger.warning(
            f"Attempt to add owner to unknown shape by {pr.player.name} [{data['shape']}]"
        )
        raise exc

    if not has_ownership(shape, pr):
        logger.warning(
            f"{pr.player.name} attempted to change asset ownership of a shape it does not own"
        )
        return

    target_user = User.by_name(data["user"])
    if target_user is None:
        logger.warning(
            f"Attempt to add unknown user as owner to shape by {pr.player.name} [{data['user']}]"
        )
        return

    # Adding the DM as user is redundant and can only lead to confusion
    if target_user == pr.room.creator:
        return

    if not ShapeOwner.get_or_none(shape=shape, user=target_user):
        ShapeOwner.create(
            shape=shape,
            user=target_user,
            edit_access=data["edit_access"],
            vision_access=data["vision_access"],
        )
    await send_client_initiatives(pr, target_user)
    await sio.emit(
        "Shape.Owner.Add",
        data,
        room=pr.active_location.get_path(),
        skip_sid=sid,
        namespace="/planarally",
    )
    if not (shape.default_vision_access or shape.default_edit_access):
        for sid in game_state.get_sids(player=target_user, room=pr.room):
            await sio.emit(
                "Shape.Set",
                shape.as_dict(target_user, False),
                room=sid,
                namespace="/planarally",
            )


@sio.on("Shape.Owner.Update", namespace="/planarally")
@auth.login_required(app, sio)
async def update_shape_owner(sid: int, data: Dict[str, Any]):
    pr: PlayerRoom = game_state.get(sid)

    try:
        shape = Shape.get(uuid=data["shape"])
    except Shape.DoesNotExist as exc:
        logger.warning(
            f"Attempt to update owner of unknown shape by {pr.player.name} [{data['shape']}]"
        )
        raise exc

    if not ShapeOwner.get_or_none(shape=shape, user=pr.player):
        logger.warning(
            f"{pr.player.name} attempted to change asset ownership of a shape it does not own"
        )
        return

    target_user = User.by_name(data["user"])
    if target_user is None:
        logger.warning(
            f"Attempt to update unknown user as owner to shape by {pr.player.name} [{data['user']}]"
        )
        return

    try:
        so = ShapeOwner.get(shape=shape, user=target_user)
    except ShapeOwner.DoesNotExist as exc:
        logger.warning(
            f"Attempt to update unknown shape-owner relation by {pr.player.name}"
        )

    so.shape = shape
    so.user = target_user
    so.edit_access = data["edit_access"]
    so.vision_access = data["vision_access"]
    so.save()

    await sio.emit(
        "Shape.Owner.Update",
        data,
        room=pr.active_location.get_path(),
        skip_sid=sid,
        namespace="/planarally",
    )


@sio.on("Shape.Owner.Delete", namespace="/planarally")
@auth.login_required(app, sio)
async def delete_shape_owner(sid: int, data: Dict[str, Any]):
    pr: PlayerRoom = game_state.get(sid)

    try:
        shape = Shape.get(uuid=data["shape"])
    except Shape.DoesNotExist as exc:
        logger.warning(
            f"Attempt to delete owner of unknown shape by {pr.player.name} [{data['shape']}]"
        )
        raise exc

    if not has_ownership(shape, pr):
        logger.warning(
            f"{pr.player.name} attempted to change asset ownership of a shape it does not own"
        )
        return

    target_user = User.by_name(data["user"])
    if target_user is None:
        logger.warning(
            f"Attempt to delete unknown user as owner to shape by {pr.player.name} [{data['user']}]"
        )
        return

    try:
        so = (
            ShapeOwner.delete()
            .where((ShapeOwner.shape == shape) & (ShapeOwner.user == target_user))
            .execute()
        )
    except Exception as e:
        logger.warning(f"Could not delete shape-owner relation by {pr.player.name}")

    await sio.emit(
        "Shape.Owner.Delete",
        data,
        room=pr.active_location.get_path(),
        skip_sid=sid,
        namespace="/planarally",
    )


@sio.on("Shape.Owner.Default.Update", namespace="/planarally")
@auth.login_required(app, sio)
async def update_default_shape_owner(sid: int, data: Dict[str, Any]):
    pr: PlayerRoom = game_state.get(sid)

    try:
        shape: Shape = Shape.get(uuid=data["shape"])
    except Shape.DoesNotExist as exc:
        logger.warning(
            f"Attempt to update owner of unknown shape by {pr.player.name} [{data['shape']}]"
        )
        raise exc

    if not has_ownership(shape, pr):
        logger.warning(
            f"{pr.player.name} attempted to change asset ownership of a shape it does not own"
        )
        return

    if "edit_access" in data:
        shape.default_edit_access = data["edit_access"]

    if "vision_access" in data:
        shape.default_vision_access = data["vision_access"]

    shape.save()

    await sio.emit(
        "Shape.Owner.Default.Update",
        data,
        room=pr.active_location.get_path(),
        skip_sid=sid,
        namespace="/planarally",
    )

    if shape.default_vision_access or shape.default_edit_access:
        for sid, player in game_state.get_users(room=pr.room):
            await sio.emit(
                "Shape.Set",
                shape.as_dict(player, player.name == pr.room.creator),
                room=sid,
                namespace="/planarally",
            )
