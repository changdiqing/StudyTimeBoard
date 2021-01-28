# external utils
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required

# internal utils
from .app_utils import *
from studytimeboard import app, db
from studytimeboard.models import User
from studytimeboard.config import backup_googlesheet
from studytimeboard.utils.database import *


@app.route('/', methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = SOMEONE

    # 0. handle the time input
    if request.method == "POST":
        if username == SOMEONE:  # user not authenticated
            username = request.form.get("username")

        if username in REGISTED_USERS:
            DataBaseAPI(backup_googlesheet=backup_googlesheet).into_from_request(request, username, db)
        else:
            flash(FlashMessages.NO_SUCH_USER, "danger")

    # if the user type in the form with duration, the next user is unknown, so the username is SOMEONE
    if not current_user.is_authenticated:
        username = SOMEONE

    df_all = get_df_all_from_db(db)

    studying_users = info_studying_users(df_all)
    no_studying_users = len(studying_users) == 0

    # 1. user previous status
    user_status, user_status_time = info_user_status(df_all, username)

    # 2. other chart info
    df_last_week = to_this_week_table(df_all)

    # prepare to plot
    # first rm the folder to avoid image database exploding
    clean_chart_folder()

    # 2.1 today's study king
    today_king, duration_str_king, path_to_chart_king = info_today_study_king(df_last_week)

    # 2.2 show the last week chart:
    # get display information
    name_winner_lw, duration_str_lw, path_to_chart_lw = info_minutes_dashboard(df_last_week, chart_prefix="lastweek",
                                                                               sep=TODAY_OR_NOT)

    return render_template('home.html',
                           studying_users=studying_users,
                           no_studying_users=no_studying_users,
                           user_status=user_status,
                           user_status_time=user_status_time,
                           path_to_chart_king=path_to_chart_king,
                           today_king=today_king,
                           duration_str_king=duration_str_king,
                           path_to_chart_lastweek=path_to_chart_lw,
                           name_winner=name_winner_lw,
                           duration_str_winner=duration_str_lw)


@app.route("/leaderboard")
def leaderboard():
    # rm the folder to avoid multiple rendering data explode
    clean_chart_folder()

    df_all = get_df_all_from_db(db)
    df_last_week = to_this_week_table(df_all)

    # get display information
    name_winner_al, duration_str_al, path_to_chart_al = info_minutes_dashboard(df_all, chart_prefix="all")
    name_winner_lw, duration_str_lw, path_to_chart_lw = info_minutes_dashboard(df_last_week, chart_prefix="lastweek",
                                                                               sep=WEEKDAY)

    return render_template('leaderboard.html',
                           path_to_chart_lastweek=path_to_chart_lw,
                           path_to_chart_all=path_to_chart_al,
                           name_winner_lastweek=name_winner_lw,
                           duration_str_lastweek=duration_str_lw,
                           name_winner=name_winner_al,
                           duration_str=duration_str_al)


@app.route('/analysis')
def analysis():
    if current_user.is_authenticated:
        username = current_user.username

        # rm the folder to avoid multiple rendering data explode
        clean_chart_folder()

        df_all = get_df_all_from_db(db)

        if username in df_all[NAME].unique():
            df_user = df_all.loc[df_all[NAME] == username, :]
            df_user_minutes = to_minutes_by_day_table(df_user)

            path_umd = path_to_chart_user_min_by_day(username)
            plot_hours_per_day(df_user_minutes, output_path=path_umd)

            path_use = path_to_chart_user_study_events(username)
            plot_study_events(df_user, output_path=path_use)

            return render_template('personal_analysis.html',
                                   username=username,
                                   path_umd=path_umd,
                                   path_use=path_use)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #    return redirect(url_for('home'))

    # form = LoginForm()
    # if form.validate_on_submit():
    if request.method == 'POST':  # this block is only entered when the form is submitted
        username = request.form.get('username')

        if username in REGISTED_USERS:
            user = User(username=username)
            login_user(user, remember=True)

            return redirect(url_for('home'))
        else:
            flash(FlashMessages.NO_SUCH_USER, "danger")
            return render_template('login.html')  # no such user

    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register')
def register():
    flash(FlashMessages.NO_SUCH_FUNC("registration"), 'danger')
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/admin_reload_data')
def admin_reload_data():
    DataBaseAPI(backup_googlesheet=backup_googlesheet).init_from_gs(db)
    return render_template('about.html')


@app.route('/admin_clean_data')
def admin_clean_data():
    # delete study events
    StudyEventDB.query.delete()
    db.session.commit()

    return render_template('about.html')


@app.route('/admin_create_some_data')
def admin_create_some_data():
    DataBaseAPI(backup_googlesheet=backup_googlesheet).into_some_examples(db)
    return render_template('about.html')
