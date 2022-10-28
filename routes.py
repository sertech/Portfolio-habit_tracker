
import datetime
import uuid
from flask import Blueprint, render_template, request, url_for, redirect, current_app

# * "habits" is the blueprint name we need for whenever we use url_for
pages = Blueprint("habits", __name__,
                  template_folder="templates", static_folder="static")


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        # (-3 4) 4 is not included
        dates = [start+datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    # * with this context_processor every jinja template will have access to a date_rage variable and that variable will contain the date_range function define above
    return {"date_range": date_range}


def today_at_midnight():
    today = datetime.datetime.today()
    # * returns an new datetime object with just year, month, and day
    # be default time,min,sec are 0
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/")
def index():
    # /?date=**** we'll try to get a argument from the url
    date_str = request.args.get("date")
    if date_str:
        # * with fromisoformat we get a date from a string
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    # * instead of a value we pass a query less than or equal to the selected date ({"$lte": selected_date})
    # * habits_on_date is a list of dictionaries
    habits_on_date = current_app.db.habits.find(
        {"added": {"$lte": selected_date}})

    # * completions is a list of habits ids
    completions = [habit["habit"]
                   for habit in current_app.db.completions.find({"date": selected_date})]

    return render_template(
        "index.html",
        habits=habits_on_date,
        title="Habit Tracker - Home",
        completions=completions,
        selected_date=selected_date,
    )


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    if request.form:  # if there is a form
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today,
             "name": request.form.get("habit")}
        )

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today_at_midnight()
    )


# @app.post("/complete") this is a shorthand
@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)
    # * current_app is the current app that is dealing with the request
    current_app.db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for("habits.index", date=date_string))
    # return redirect(url_for(".index", date=date_string)) # .index means the current blueprint dot and index function within that
