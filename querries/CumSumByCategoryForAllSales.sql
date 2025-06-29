WITH CombinedSales AS (
    SELECT 
        dpc.EnglishProductCategoryName AS Category,
        dd.FullDateAlternateKey AS OrderDate,
        sum(fis.SalesAmount) AS Sales
    FROM FactInternetSales fis
    JOIN DimProduct dp ON dp.ProductKey = fis.ProductKey
    JOIN DimProductSubcategory dpsc ON dpsc.ProductSubcategoryKey = dp.ProductSubcategoryKey
    JOIN DimProductCategory dpc ON dpc.ProductCategoryKey = dpsc.ProductCategoryKey
    JOIN DimDate dd ON dd.DateKey = fis.OrderDateKey
    where dpc.ProductCategoryKey = 1
    GROUP BY dpc.EnglishProductCategoryName, dd.FullDateAlternateKey
    UNION ALL
    SELECT 
        dpc.EnglishProductCategoryName,
        dd.FullDateAlternateKey,
        sum(frs.SalesAmount)
    FROM FactResellerSales frs
    JOIN DimProduct dp ON dp.ProductKey = frs.ProductKey
    JOIN DimProductSubcategory dpsc ON dpsc.ProductSubcategoryKey = dp.ProductSubcategoryKey
    JOIN DimProductCategory dpc ON dpc.ProductCategoryKey = dpsc.ProductCategoryKey
    JOIN DimDate dd ON dd.DateKey = frs.OrderDateKey
    where dpc.ProductCategoryKey = 1
    GROUP BY dpc.EnglishProductCategoryName, dd.FullDateAlternateKey
),
DailySales AS (
    SELECT
        Category,
        OrderDate,
        SUM(Sales) AS TotalDailySales
    FROM CombinedSales
    GROUP BY Category, OrderDate
)
SELECT
    Category,
    OrderDate,
    TotalDailySales,
    SUM(TotalDailySales) OVER (
        PARTITION BY Category 
        ORDER BY OrderDate
    ) AS CumulativeSales
FROM DailySales
ORDER BY Category, OrderDate;
