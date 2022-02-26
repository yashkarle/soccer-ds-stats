import pandas as pd
import streamlit as st


data = pd.read_csv('/Users/yashkarle/soccer-ds-stats/Viz/1PlayerScouting/data/epl-possession.csv')

data['Nation'] = data['Nation'].str.split(' ', expand=True)[1]
data['Pos'] = data['Pos'].str[:2]
data['Age'] = data['Age'].str.split('-', expand=True)[0]


cbs_list = [
    'Virgil van Dijk', 'Thiago Silva', 'Aymeric Laporte', 'Rúben Dias', 'Antonio Rüdiger', 'Raphaël Varane',
    'James Tarkowski', 'Tyrone Mings', 'John Stones', 'Ibrahima Konaté', 'Andreas Christensen', 'Trevoh Chalobah', 'Malang Sarr',
    'Mason Holgate', 'Angelo Ogbonna', 'Harry Maguire', 'Ben Mee', 'Joël Matip', 'Kurt Zouma', 'Jonny Evans', 'Gabriel Dos Santos',
    'Cristian Romero', 'Joe Gomez', 'Ben White', 'Nathan Aké', 'Eric Dier', 'Conor Coady', 'Victor Lindelöf', 'Ezri Konsa', 'Ben Godfrey',
    'Jannik Vestergaard', 'Mohammed Salisu', 'Eric Bailly', 'Kristoffer Ajer', 'Yerry Mina', 'Rob Holding', 'Michael Keane', 'Jamaal Lascelles',
    'Kortney Hause', 'Jan Bednarek', 'Joachim Andersen', 'Lewis Dunk', 'Grant Hanley', 'Phil Jones', 'Craig Dawson', 'Pontus Jansson',
    'Liam Cooper', 'Craig Cathcart', 'Federico Fernández', 'Ethan Pinnock', 'Çağlar Söyüncü', 'Issa Diop', 'Pascal Struijk', 'Marc Guéhi', 'Max Kilman',
    'Joe Rodon', 'Japhet Tanganga', 'Romain Saïss', 'Daniel Amartey', 'Ciaran Clark', 'Diego Llorente', 'Robin Koch', 'Davinson Sánchez', 'Dan Burn'
]
data = data[(data['Player'].isin(cbs_list)) & (data['90s'] >= 5)]

calc_elements = ['Carries_Prog', 'Carries_PrgDist', 'Rec_Prog']
for each in calc_elements:
    data[f'{each}_p90'] = data[each] / data['90s']

teams = list(data['Squad'].drop_duplicates())
teams_choice = st.sidebar.multiselect("Teams:", teams, default=teams)
age_choice = st.sidebar.slider('Max Age:', min_value=16, max_value=40, step=1, value=40)

data = data[data['Squad'].isin(teams_choice)]
data = data[data['Age'].astype(int) < age_choice]


st.title(f"Which Centre Backs contribute most to the Build-up Phase?")
st.markdown('### Data points as sourced from FBref')

display_cols = ['Player', 'Nation', 'Squad', 'Age', '90s', 'Touches', 'Dribbles_Succ',
                # 'Carries_Prog_p90', 'Carries_PrgDist_p90', 'Rec_Prog_p90',
                'Carries', 'Carries_PrgDist', 'Carries_Prog', 'Carries_Final3rd', 'Carries_CPA',
                'Rec_Targ', 'Rec', 'Rec_Prog']
st.dataframe(data[display_cols].sort_values('Squad').reset_index(drop=True))

st.markdown('### Passing Directness : Premier League 2021-22')
st.vega_lite_chart(data, {
    'mark': {'type': 'circle', 'tooltip': True},
    'encoding': {
        'x': {'field': 'Carries_PrgDist_p90', 'type': 'quantitative'},
        'y': {'field': 'Carries_Prog_p90', 'type': 'quantitative'},
        'color': {'field': 'Squad', 'type': 'nominal'},
        'tooltip': [{"field": 'Player', 'type': 'nominal'},
                    {'field': 'Carries_PrgDist_p90', 'type': 'quantitative'},
                    {'field': 'Carries_Prog_p90', 'type': 'quantitative'}],
    },
    'width': 700,
    'height': 400,
})
