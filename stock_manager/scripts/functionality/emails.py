import smtplib
from datetime import datetime
from email.message import EmailMessage

body = ('Hello,\n\n'
        
        'This is an automatic notification detailing that '
        'the following item has reached a total stock of 0:\n'
        '\tItem: PART_NUM\n'
        '\tDescription: DESCRIPTION\n'
        '\tExcess Count: EXCESS (STATUS)\n'
        f'\tDate/Time: {datetime.now()}\n\n'
        
        'Please take any necessary action to reorder or restock.\n\n'
        
        'Best regards,\n'
        'Stock Management System')

msg = EmailMessage()
msg.set_content(body)
msg['subject'] = 'Common Stock Notification'
msg['to'] = 'lkingerslev@gmail.com'

user = 'common.stock.notifications@gmail.com'
msg['from'] = user
password = 'uzxlkxbxewhmakwi'

server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20)
server.login(user, password)

server.send_message(msg)

server.quit()
