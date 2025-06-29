 select distinct
	dd.calendaryear as Year,
	dd.calendarsemester as Semester,
	dc.customerkey as CustomerKey,
	dc.emailaddress as Email,
	dc.firstname as FirstName,
	dc.lastname as LastName
from FactInternetSales as fis
join DimCustomer dc on(dc.customerkey = fis.customerkey)
join DimDate dd on(dd.datekey = fis.orderdatekey)
where dd.calendaryear = 2013 and dd.calendarsemester = 1
order by dc.customerkey
