from flask import jsonify


def serialize_post(obj):
    return jsonify(
        author=str(obj.author),
        title=obj.title,
        tags=", ".join([str(t) for t in obj.tags]),
        slug=obj.slug,
        created_on=obj.created_on
    )
