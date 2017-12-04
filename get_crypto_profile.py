# Uses cryptocompare API to get current price of altcoins: https://www.cryptocompare.com/api/#
# Uses coindesk API to get bitcoin's value https://www.coindesk.com/api/
# Uses coinmarketcap for MIOTA https://api.coinmarketcap.com/v1/ticker/iota

# to test email run: python -m smtpd -n -c DebuggingServer localhost:1025

import json
import urllib.request
import pandas as pd
import smtplib

def send_email(total_usd, total_profit, df, time):
	server = "localhost"
	from_email = "example@example.com"
	to_email = ["example@example.com"] # must be a list
	subject = "Cryptocurrency Portfolio Performance"
	text = "As of " + str(time) + " cryptocurrency balances are valued at " + '${:,.2f}'.format(total_usd) + " representing a profit of " + '${:,.2f}'.format(total_profit)  + " since initial investment."

	# Prepare actual message
	message = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (from_email, ", ".join(to_email), subject, text)

	# Send the mail
	server = smtplib.SMTP('localhost', port =1025)
	server.sendmail(from_email, to_email, message)
	server.quit()

def get_currency_portfolio(write_output = 0):
	response = urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
	time = btc_in_usd = 0
	if response is not None:
		response = json.load(response)
		time = response['time']['updated']
		btc_in_usd = response["bpi"]["USD"]["rate"]

	if write_output == 1:
		print("Updating portfolio at: "  + str(time) + " when BTC = $" + str(btc_in_usd) )

	historical_data = json.load(open('coin_history.json'))

	coins_df = pd.DataFrame(columns=['Coin', 'Original Value (BTC)','Current Value (BTC)', 'Profit (BTC)', 'Original Value (USD)', 'Current Value (USD)', 'Profit (USD)'])


	for coin in historical_data:
		coin_name = coin['coin'] #coin symbol
		btc_per_coin_org = coin['btc_per_coin'] # BTC per 1 coin at time of purchase
		usd_per_btc_org = coin['usd_per_btc'] #BTC to USD at the time of purchase
		num_coins = coin['num_coins'] #number of coins bought

		# Original cost of coins in BTC and USD
		org_value_btc = float(btc_per_coin_org) * num_coins
		org_value_usd = float(btc_per_coin_org) * float(usd_per_btc_org) * num_coins
		
		if coin_name == "MIOTA":
			cur_prices = json.load(urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/iota"))
			cur_value_btc = float(cur_prices[0]['price_btc']) * num_coins
			cur_value_usd = float(cur_prices[0]['price_usd']) * num_coins
			
		else:
			cur_prices = json.load(urllib.request.urlopen("https://min-api.cryptocompare.com/data/price?fsym=" + str(coin_name) +"&tsyms=BTC,USD"))
			
			# Current value of coin in BTC and USD
			cur_value_btc = cur_prices['BTC'] * num_coins
			cur_value_usd = cur_prices['USD'] * num_coins

		# Profits/losses
		diff_btc = cur_value_btc - org_value_btc
		diff_usd = cur_value_usd - org_value_usd

		coins_df.loc[len(coins_df)] = [coin_name, org_value_btc, cur_value_btc, diff_btc, org_value_usd, cur_value_usd, diff_usd ]

	profit_total_usd = coins_df['Profit (USD)'].sum()
	orig_total_usd = coins_df['Original Value (USD)'].sum()
	cur_total_usd = coins_df['Current Value (USD)'].sum()
	perc_growth_total = (abs(orig_total_usd - cur_total_usd)/orig_total_usd)*100

	if write_output == 1:
		print(coins_df)
		print("Total profit: " +'${:,.2f}'.format(profit_total_usd))
		print("Original total: " + '${:,.2f}'.format(orig_total_usd))
		print("Current total: " + '${:,.2f}'.format(cur_total_usd))
		print("Percent growth: " + '{:,.2f}%'.format(perc_growth_total))

	send_email(total_usd = cur_total_usd, total_profit = profit_total_usd, df = coins_df, time = time)
	return cur_total_usd





if __name__ == "__main__":
	get_currency_portfolio(write_output = 1)
