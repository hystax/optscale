from mongoengine import (
    Document,
    IntField,
    StringField,
    ReferenceField,
    DENY,
    BooleanField,
)


class Event(Document):
    time = IntField(required=True)
    level = StringField(max_length=64, required=True)
    evt_class = StringField(max_length=32, required=True)
    object_id = StringField(max_length=36, required=False)
    object_type = StringField(max_length=64, required=False)
    object_name = StringField(max_length=256, required=False)
    organization_id = StringField(max_length=36, required=True)
    description = StringField(required=False)
    ack = BooleanField(required=True)
    acknowledged = IntField(required=False)
    acknowledged_by = StringField(max_length=32, required=False)
    acknowledged_user = StringField(required=False)
    resolution = StringField(max_length=256, required=False)
    localized = StringField(required=False)
    initiator_id = StringField(max_length=36, required=False)
    initiator_name = StringField(required=False)

    meta = {"indexes": [{"fields": ["-time"]}]}

    def to_dict(self):
        obj_dict = self.to_mongo().to_dict()
        del obj_dict["_id"]
        obj_dict.update({"id": str(self.id)})
        return obj_dict


class ReadEvent(Document):
    user_id = StringField(max_length=36, required=True)
    event = ReferenceField(Event, reverse_delete_rule=DENY)


class Feedback(Document):
    email = StringField(max_length=256, required=True)
    time = IntField(required=True)
    text = StringField(required=True)
    metadata = StringField(required=False)
    url = StringField(required=False)
    user_id = StringField(max_length=36, required=False)

    meta = {"indexes": [{"fields": ["-time"]}]}

    def to_dict(self):
        obj_dict = self.to_mongo().to_dict()
        del obj_dict["_id"]
        obj_dict.update({"id": str(self.id)})
        return obj_dict
