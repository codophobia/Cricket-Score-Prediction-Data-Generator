from bs4 import BeautifulSoup
from collections import OrderedDict
import os
import csv
import json
import sys
import sys
import datetime

c = 0
flag = 0

csvfile = open('t20.csv','w')
def create_dataset(full,total,win):
	# The output csv will be stored in file name result.
	spamwriter = csv.writer(csvfile, delimiter=',',
							quoting=csv.QUOTE_MINIMAL)
	global flag
	for r in full:
		if(flag == 0):
			spamwriter.writerow(["mid", "date","venue","format","tournament","gender","bat_team","bowl_team","batsman","bowler","runs","wickets","overs","runs_last_5","wickets_last_5","striker","non-striker","total","win"])
			flag = 1
		spamwriter.writerow([r[0], r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],r[13],r[14],r[15],r[16],total,win])

def scorecard():

	"""
	This functions was intended to generate a scorecard of a match. Later, some more code
	was added to create a dataset for score prediction.
	"""

	cnt = 0
	c = 0

	ballcnt = 0
	folders = os.listdir('../data') # Keep all the files inside the data folder
	for folder in sorted(folders):
		files = os.listdir(f'../data/{folder}')
		for file in sorted(files):
			if 'xml' not in file:
				continue
			path =  f'../data/{folder}/{file}'
			print(path)
			mid = file.split('.')[0]
			if(True): # Don't remember why I have written this :(
				content = open(path)
				soup = BeautifulSoup(content,"lxml")
				data = {}
				match = {}
				info = soup.find('info')
				teams = info.find('teams').find_all('team')
				team1 = teams[0].get_text()
				team2 = teams[1].get_text()
				mtype = info.find('match_type').get_text()
				venue = info.find('venue').get_text()
				outcome = info.find('outcome')

				try:
					winner = outcome.find('winner').get_text()
				except:
					winner = outcome.find('result')
					if(winner):
						winner = outcome.find('result').get_text()
					else:
						winner = outcome.get_text()
				try:
					result = outcome.find('result').get_text()
					# Remove the comments if you do not want matches with no result
					'''if(result == "no result"):
						print result
						continue'''
				except:
					pass

				try:
					result = outcome.find('method').get_text()
					# Remove the comments if you do not want matches with D/L
					'''if(result == "D/L"):
						print result
						continue'''
				except:
					pass
				try:
					city = info.find('city').get_text()
				except:
					city = ""
				date = info.find('dates').find('date').get_text()
				innings = soup.find('innings').find_all('inning')
				try:
					pp = info.find('player_of_match').find('player_of_match').get_text()
				except:
					pp = ""
				try:
					comp = info.find('competition').get_text()
				except:
					comp = ""
				gender = info.find('gender').get_text()
				match['teams'] = str(team1 + " vs " + team2)
				match['mtype'] = str(mtype)
				if city:
					match['city'] = str(city)
				match['date'] = str(date)
				if venue:
					match['venue'] = str(venue)
				if pp:
					match['mom'] = str(pp)


				match['id'] = mid
				data['matchinfo'] = match
				inning_cnt = 0
				first_inning_total = 0
				inning_list = []
				c += 1

				# Only men t-20 will be processed
				if mtype != 'T20' or gender != 'male':
					continue

				for inning in innings:
					inning_cnt += 1
					dinning = {}
					deliveries = inning.find('deliveries').find_all('delivery')
					cnt = 0
					ino = int(inning.find('inningsnumber').get_text())
					bat_team = inning.find('team').get_text()
					bowl_team = team1
					if bat_team == team1:
						bowl_team = team2
					bat = OrderedDict()
					bowl = OrderedDict()
					total = 0
					total_overs = 0
					total_wickets = 0
					over_runs = 0
					balls = 0
					maiden = 0
					over_no = 0
					is_last_ball = 0
					full = []

					for d in deliveries:
						batsman = d.find('batsman').get_text()
						bowler = d.find('bowler').get_text()
						non_striker = d.find('non_striker').get_text()
						bruns = int(d.find('runs').find('batsman').get_text())
						truns = int(d.find('runs').find('total').get_text())
						eruns = int(d.find('runs').find('extras').get_text())
						over = int(d.find('over').get_text())
						cball = int(d.find('ball').get_text())
						wide = 0
						noball = 0
						bye = 0
						legbye = 0
						iswicket = 0
						ballcnt += 1
						extra_flag = 0
						wckt_flag = 0

						e_type = ''

						# Parsing extras
						if d.find('extras') is not None:
							if d.find('extras').find('wides') is not None:
								wide = 1
								e_type = "wide"
							elif d.find('extras').find('noballs') is not None:
								noball = 1
								e_type = "no ball"
							elif d.find('extras').find('byes') is not None:
								bye = 1
								e_type = "byes"
							elif d.find('extras').find('legbyes') is not None:
								e_type = "leg byes"
							else:
								e_type = d.find('extras').contents[0].name
							extra_flag = 1

						# Calculate information for bowler and batsman
						if batsman not in bat:
							bat[batsman] = {'runs':0,'balls':0,'fours':0,'six':0,'dismissal':'not out'}
						if non_striker not in bat:
							bat[non_striker] = {'runs':0,'balls':0,'fours':0,'six':0,'dismissal':'not out'}
						if bowler not in bowl:
							bowl[bowler] = {'overs':0,'maiden':0,'runs':0,'wickets':0}
						bat[batsman]['runs'] += bruns
						if wide == 0:
							bat[batsman]['balls'] += 1
						if bruns == 4:
							bat[batsman]['fours'] += 1
						if bruns == 6:
							bat[batsman]['six'] += 1
						total += truns
						if bye == 1 or legbye == 1:
							over_runs += bruns
							bowl[bowler]['runs'] += bruns
						else:
							over_runs += truns
							bowl[bowler]['runs'] += truns
						if wide == 0 and noball == 0:
							cnt += 1
							balls += 1
							bowl[bowler]['overs'] += 1
						current_ball = float(str(over) + "."  + str(cball))

						if balls == 6:
							total_overs += 1
							over_no += 1
							if over_runs == 0:
								maiden = 1
							over_runs = 0
							bowl[bowler]['maiden'] += maiden
							maiden = 0
							balls = 0
							is_last_ball = 1

						run_rate_ball = float(str(total_overs) + "."  + (str(balls/6.0)).split('.')[1])
						player_out = ''
						w_type = ''
						fielder = None

						# Parsing wickets
						if d.find('wickets') is not None:
							s = ""
							iswicket = 1

							w = d.find('wickets').find('wicket')
							if w.find('kind'):
								s = s + w.find('kind').get_text() + " "
							if w.find('fielders'):
								s = s + w.find('fielders').find('fielder').get_text() + " "
								fielder = w.find('fielders').find('fielder').get_text()
							if w.find('kind').get_text() != 'run out':
								if w.find('kind').get_text() != 'bowled' and w.find('kind').get_text() != 'hit wicket':
									s = s + "bowled" + " " +  bowler
								else:
									s = s + bowler
								bowl[bowler]['wickets'] += 1
							player_out = w.find('player_out').get_text()
							w_type = w.find('kind').get_text()
							#bat[player_out]['dismissal'] = str(s)
							total_wickets += 1
							wckt_flag = 1


						if(iswicket):
							if(player_out == batsman):
								s1 = bat[non_striker]['runs']
							else:
								s1 = bat[batsman]['runs']
							s2 = 0
						s1 = max(bat[batsman]['runs'],bat[non_striker]['runs'])
						s2 = min(bat[batsman]['runs'],bat[non_striker]['runs'])


						current_rr = float(total/max(run_rate_ball,0.16))
						current_rr = format(current_rr, '.2f')

						# This is for calculating last 5 overs data
						if(len(full) >= 30 ):
							last_5_runs = total - full[-30:][0][10]
							last_5_wickets = total_wickets-full[-30:][0][11]
							last_5_rr = float(last_5_runs/5.0)
							last_5_rr = format(last_5_rr, '.2f')
						else:
							last_5_runs = total
							last_5_wickets = total_wickets
							last_5_rr = current_rr
						win = 0
						if(bat_team == winner):
							win = 1
						full.append((c,date,venue,mtype,comp,gender,bat_team,bowl_team,batsman,bowler,total,total_wickets,current_ball,last_5_runs,last_5_wickets,s1,s2))
					if(inning_cnt == 2):
						create_dataset(full,first_inning_total,win)
					if(inning_cnt == 1):
						first_inning_total = total
					if balls != 0:
						total_overs = float(str(total_overs) + "." + str(balls))

scorecard()
