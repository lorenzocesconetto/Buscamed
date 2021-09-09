SELECT * FROM product_detail_click;
SELECT * FROM searches ORDER BY timestamp DESC;
SELECT COUNT(*) FROM searches WHERE timestamp > '2021-03-07';
SELECT ean, COUNT(*) AS clicks FROM product_detail_click GROUP BY ean ORDER BY clicks DESC;

SELECT * FROM item WHERE ean=7896015518875;
SELECT * FROM item WHERE ean=7896422526975;