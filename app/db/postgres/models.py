from .connection import db


class File(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(255))
    size = db.Column(db.Integer, nullable=False)
    filepath = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    modified_at = db.Column(db.DateTime)
    comment = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "extension": self.extension,
            "size": self.size,
            "filepath": self.filepath,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "comment": self.comment,
        }


class Session(db.Model):
    session_id = db.Column(db.String(36), primary_key=True)
