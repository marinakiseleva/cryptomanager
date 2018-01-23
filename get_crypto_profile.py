# Uses cryptocompare API to get current price of altcoins: https://www.cryptocompare.com/api/#
# Uses coindesk API to get bitcoin's value https://www.coindesk.com/api/
# Uses coinmarketcap for MIOTA https://api.coinmarketcap.com/v1/ticker/iota



import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from datetime import datetime 


def get_currency_portfolio(print_output = 0, show_plot = 0, data_file):
	historical_data = json.load(open(data_file))
	coins_df = pd.DataFrame(columns=['Coin', 'Original Value (BTC)','Current Value (BTC)', 'Profit (BTC)', 'Original Value (USD)', 'Current Value (USD)', 'Profit (USD)', 'Number Of Coins', 'Value of Coin (USD)'])

	for coin in historical_data:
		coin_name = coin['coin'] #coin symbol
		btc_per_coin_org = coin['btc_per_coin'] # BTC per 1 coin at time of purchase
		usd_per_btc_org = coin['usd_per_btc'] #BTC to USD at the time of purchase
		num_coins = coin['num_coins'] #number of coins bought

		if coin_name is None or num_coins is None:
			raise ValueError('Must provide Coin Name (coin_name) and Number of coins (num_coins) for each JSON item in ' + data_file)

		
		# Get current value of coin from APIs
		usd_per_coin = btc_per_coin = 0
		if coin_name == "MIOTA":
			cur_prices = json.load(urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/iota"))
			btc_per_coin = float(cur_prices[0]['price_btc'])
			usd_per_coin = float(cur_prices[0]['price_usd'])
			
		else:
			cur_prices = json.load(urllib.request.urlopen("https://min-api.cryptocompare.com/data/price?fsym=" + str(coin_name) +"&tsyms=BTC,USD"))
			btc_per_coin = cur_prices['BTC']
			usd_per_coin = cur_prices['USD']

		# Total current value of coins in BTC and USD
		cur_value_btc = btc_per_coin * num_coins
		cur_value_usd = usd_per_coin * num_coins
		
		# Total original value of coins in BTC and USD
		org_value_btc = float(btc_per_coin_org) * num_coins
		org_value_usd = float(btc_per_coin_org) * float(usd_per_btc_org) * num_coins

		# Profits/losses
		diff_btc = cur_value_btc - org_value_btc
		if org_value_usd != 0:
			diff_usd = cur_value_usd - org_value_usd
			perc_growth = (abs(org_value_usd - cur_value_usd)/org_value_usd)*100	
		else:
			diff_usd = perc_growth = 0
		

		coins_df.loc[len(coins_df)] = [coin_name, org_value_btc, cur_value_btc, diff_btc, org_value_usd, cur_value_usd, diff_usd, num_coins, '${:,.2f}'.format(usd_per_coin)]

	profit_total_usd = coins_df['Profit (USD)'].sum()
	orig_total_usd = coins_df['Original Value (USD)'].sum()
	cur_total_usd = coins_df['Current Value (USD)'].sum()
	



	if print_output == 1:
		cur_price = json.load(urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/bitcoin"))
		
		if cur_price is not None:
			cur_price = float(cur_price[0]['price_usd']) if cur_price is not None else 'Price unavailable.'
		print("Updating portfolio at: "  + str(datetime.now()) + " when BTC = " + '${:,.2f}'.format(cur_price))

		pd.options.display.width = 880
		coins_df = coins_df.sort_values(['Current Value (USD)'], ascending=False)
		print(coins_df[['Coin', 'Original Value (USD)', 'Current Value (USD)', 'Profit (USD)', 'Number Of Coins', 'Value of Coin (USD)']])
		print("Total Cryptocurrency: " + '${:,.2f}'.format(cur_total_usd))
		print("Alt Total profit: " +'${:,.2f}'.format(profit_total_usd))
		print("Alt Original total: " + '${:,.2f}'.format(orig_total_usd))
		


	if show_plot == 1:
		plot = coins_df[['Current Value (USD)', 'Profit (USD)']].plot(kind='bar', title='Coin Values (USD)', legend=True, width = .7, figsize=[12,7])
		plot.set_xlabel("Coin", fontsize=12)
		plot.set_xticklabels(coins_df.Coin)
		plot.set_ylabel("Vaue (USD)", fontsize=12)

		for patch in plot.patches:
		    bl = patch.get_xy()
		    x = 0.5 * patch.get_width() + bl[0]
		    y = 0.92 * patch.get_height() + bl[1] 
		    plot.text(x,y,"%d" %(patch.get_height()), ha='center', rotation='vertical', weight = 'light', fontsize=10)

		plt.show()
	return cur_total_usd






if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-print_output',  type=int, default=1, help='Print dataframe output.')
	parser.add_argument('-show_plot', type=int, default=0, help='Display plot of assets growth.')
	parser.add_argument('-data_file', type=str, default='coin_history.json', help='Name of JSON file (including .json) that contains cryptocurrency data.')
	args = parser.parse_args()
	get_currency_portfolio(print_output = args.print_output, show_plot = args.show_plot, data_file = args.data_file)




