import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()
    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )


@app.route("/tags/<tag_id>/update_note",methods=["GET", "POST"])
def update_note(tag_id):
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag_id))
    ).scalars().first()

    form = forms.NoteForm()
    form_title = notes.title
    form_description = notes.description
    if not form.validate_on_submit():
        print(form.errors)
        return flask.render_template("update_note.html",form=form,form_title=form_title,form_description=form_description)
    
    note = models.Note(id=tag_id)
    form.populate_obj(note)
    notes.description = form.description.data
    notes.title = form.title.data
    db.session.commit()

    return flask.redirect(flask.url_for("index"))

@app.route("/tags/<tag_id>/update_tags",methods=["GET", "POST"])
def update_tags(tag_id):
    db = models.db
    tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
            .scalars()
            .first()
        )

    form = forms.TagsForm()
    form_name = tag.name

    if not form.validate_on_submit():
        print(form.errors)
        return flask.render_template("update_tags.html",form=form,form_name=form_name)
    
    note = models.Note(id=tag_id)
    form.populate_obj(note)
    tag.name = form.name.data
    db.session.commit()

    return flask.redirect(flask.url_for("index"))

@app.route("/tags/<tag_id>/delete_note",methods=["GET", "POST"])
def delete_note(tag_id):
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag_id))
    ).scalars().first()
    notes.description = ""
    db.session.commit()

    return flask.redirect(flask.url_for("index"))



@app.route("/tags/<tag_id>/delete_tags",methods=["GET", "POST"])
def delete_tags(tag_id):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    tag.name = ""
    db.session.commit()

    return flask.redirect(flask.url_for("index"))

@app.route("/tags/<tag_id>/delete",methods=["GET", "POST"])
def delete(tag_id):
    db = models.db

    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag_id))
    ).scalars().first()
    
    db.session.delete(notes)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
