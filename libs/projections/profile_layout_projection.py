def layout_data(layout):
    return {
        "id": layout.id,
        "name": layout.name,
        "profile_picture_x": layout.profil_picture_x,
        "profile_picture_y": layout.profil_picture_y,
        **{key: getattr(layout, key) for key in (
            "name_x", "name_y", "username_x", "username_y", "level_x",
            "level_y", "badge_x", "badge_y", "level_bar_x", "level_bar_y"
        )},
    }
