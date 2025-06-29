select
	dd.calendaryear as Year,
	dd.calendarquarter as Quarter,
	dr.resellername as Seller,
	sum(frs.orderquantity) as SellCount
from factresellersales frs
join dimreseller dr on(dr.resellerkey  = frs.employeekey)
join dimdate dd on(frs.orderdatekey = dd.datekey)
where dd.calendaryear = 2012 and dd.calendarquarter = 2
group by dr.resellername, dd.calendaryear, dd.calendarquarter
having sum(frs.orderquantity)>1000
order by SellCount