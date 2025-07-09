from flask import Flask, jsonify

from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
import pandas as pd
from api import fetch_and_store_fixtures, get_team_fixtures
from forms import TeamForm, RegistrationForm

app = Flask(__name__)
proxied = FlaskBehindProxy(app)

app.config['SECRET_KEY'] = '64308e59a504487c29241789d2a3b32c'

@app.route("/")
def home():
    return render_template('home.html', title='Home')

@app.route("/team", methods=['GET', 'POST'])
def team():
    form = TeamForm()
    if form.validate_on_submit():
        team_name = form.team_name.data
        try:
            fixtures = get_team_fixtures(team_name)
            print("DEBUG: fixtures type =", type(fixtures))

            # Fallback: if fixtures is a list, convert manually
            if isinstance(fixtures, list):
                fixtures = pd.DataFrame(fixtures, columns=['utcDate', 'Home', 'Away', 'Status', 'Score_H', 'Score_A'])

        except Exception as e:
            flash(f"Error fetching fixtures: {e}", 'danger')
            fixtures = pd.DataFrame(columns=['utcDate', 'Home', 'Away', 'Status', 'Score_H', 'Score_A'])
        
        return render_template('fixtures.html', team_name=team_name, fixtures=fixtures.to_dict(orient='records'))

    return render_template('team.html', title='Team Fixtures', form=form)

    

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)



    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")