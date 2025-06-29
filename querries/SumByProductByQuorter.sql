
SELECT
    filtered_data.Year as Year,
    filtered_data.Quorter as Quorter, 
    filtered_data.EnglishProductName as ProductName,
    SUM(filtered_data.SalesAmount) AS TotalSalesAmount
FROM (
    SELECT 
        dd.CalendarYear AS Year,
        dd.CalendarQuarter AS Quorter,
        dp.EnglishProductName,
        fis.SalesAmount
    FROM DimProduct dp
    JOIN FactInternetSales fis ON fis.ProductKey = dp.ProductKey
    JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE dd.CalendarYear = 2010 AND dd.CalendarQuarter = 4
    
    UNION ALL

    SELECT 
        dd.CalendarYear,
        dd.CalendarQuarter,
        dp.EnglishProductName,
        frs.SalesAmount
    FROM DimProduct dp
    JOIN FactResellerSales frs ON frs.ProductKey = dp.ProductKey
    JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE dd.CalendarYear = 2010 AND dd.CalendarQuarter = 4
) filtered_data
GROUP BY 
    EnglishProductName, 
    Year, 
    Quorter
ORDER BY 
    TotalSalesAmount DESC;
		
	