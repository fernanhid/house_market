import feedparser
from flask import Flask, render_template
from flask import request
import pandas as pd
import numpy as np
import pickle
from flask_bootstrap import Bootstrap
import json
import requests
from flask_googlemaps import GoogleMaps, Map
from sqlalchemy import create_engine



app = Flask(__name__)

bootstrap = Bootstrap(app)

GoogleMaps(app)


defaults = {'town': 'Englewood',
			'bed': 1,
			'bath': 1,
			'sqft': 700,
			'if_studio': 0,
			'lat': 40.8927778,
			'lng': -73.9730556,
			'address': '350 Engle Street',
			'Air Conditioning': 0, 
			'Cable Ready': 0,
			 'Deck': 0, 
			 'Dishwasher': 0,
       		'High Speed Internet Access': 0, 
       		'Laundry Facility': 0, 
       		'Microwave': 0,
       		'Pets OK': 0,
       		 'Refrigerator': 0, 
       		 'Washer/Dryer in Unit': 0}

reg_model = pickle.load(open('amenities_model.pkl', 'rb'))

bed_nums = [1,2,3]
bath_nums = [1,2,3,4]

with open ('townlist.list', 'rb') as fp:
    town_names = pickle.load(fp)

town_types_dict  = {town:i for (i, town) in enumerate(town_names)}

#House map Stuff
engine = create_engine('postgresql://postgres:1Pedromachuca@localhost:5432/dvd')

to_erase = pd.read_sql_query('select * from map_info;', engine)
to_erase = to_erase[to_erase.columns.difference(['index'])]
house_map_data = to_erase.values

house_locations = []

for crime in house_map_data:
    named_crime = {
    'lat': crime[1],
    'lng': crime[0],
    #crime3 is name and crime4 is url
    'infobox': '%s<br>%s'%(crime[2],crime[3])
    }
    house_locations.append(named_crime)

#Start of Templates                                     

@app.route('/')
def home():
 

	beds = get_values('bed')

	baths = get_values('bath')

	sqft = get_values('sqft')

	if_studio = get_values('if_studio')

	town = get_values('town')

	address = get_values('address')

	lat, lng = call_api(address, town)

	#test
	#value = request.form.getlist('check') 

	ac = get_values('Air Conditioning') 
	cable = get_values('Cable Ready')
	deck = get_values('Deck')
	dishw = get_values('Dishwasher')
	wifi = get_values('High Speed Internet Access')
	laundry_f = get_values('Laundry Facility')
	microw = get_values('Microwave')
	if_pets = get_values('Pets OK')
	fridge = get_values('Refrigerator')
	wash_dry_unit = get_values('Washer/Dryer in Unit')


	amenities_list = ['Air Conditioning','Cable Ready','Deck','Dishwasher','High Speed Internet Access',
	'Laundry Facility','Microwave','Pets OK','Refrigerator','Washer/Dryer in Unit']


	x = pd.Series(np.zeros(28))
	x.iloc[24] = baths
	x.iloc[25] = beds
	x.iloc[26] = if_studio
	x.iloc[27] = sqft
	x.iloc[town_types_dict[town]] = 1

	x.iloc[14] = ac
	x.iloc[15] = cable
	x.iloc[16] = deck
	x.iloc[17] = dishw
	x.iloc[18] = wifi
	x.iloc[19] = laundry_f
	x.iloc[20] = microw
	x.iloc[21] = if_pets
	x.iloc[22] = fridge
	x.iloc[23] = wash_dry_unit

	prediction = np.exp(reg_model.predict(x.reshape(1, -1))[0])



	test_map = Map(identifier="test_map",lat=lat,lng=lng,markers= house_locations,
				style = "height:500px;width:100%;margin:0;")



	return render_template('heroku_market.html', prediction = prediction,
							town_names = town_names, bed_nums = bed_nums, bath_nums = bath_nums,
							sqft = sqft, test_map = test_map, amenities_list = amenities_list)

def get_values(query):
	output = request.args.get(query)
	if not output:
		output = defaults[query]
	return output

def call_api(address, town):
	api_address = address.replace(' ', '+')
	api_town = '+' + town.replace(' ', '+')

	api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s,%s,+NJ'%(api_address,api_town)

	response = requests.get(api_url, verify = False).json()['results'][0]['geometry']['location']

	return response['lat'], response['lng']

# def new_map(lat_,lng_, house_locations):

# 	sndmap = Map(
#         identifier="sndmap",
#         lat=lat_,
#         lng=-lng_,
#         markers= house_locations)

#     return sndmap



 if __name__ == '__main__':
     app.debug = True
     port = int(os.environ.get("PORT", 5000))
     app.run(host='0.0.0.0', port=port)