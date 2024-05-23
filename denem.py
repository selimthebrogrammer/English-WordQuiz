import datetime


trh1 = datetime.date.today()
trh2= trh1 + datetime.timedelta(days=1)
print(trh1,trh2)

fark = trh1-trh2
fark = fark.days
fark = abs(fark)
print(fark)