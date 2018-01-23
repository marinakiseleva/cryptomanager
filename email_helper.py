import smtplib
# to test email run: python -m smtpd -n -c DebuggingServer localhost:1025
def send_email(total_usd, total_profit, time):
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