-- SELECT * FROM store;

-------------------------------------------------
-- UPDATE item SET is_active=true WHERE timestamp > '2021-02-26';

-- SELECT count(*) FROM public.item;
-- SELECT count(*) FROM public.item WHERE requires_prescription;
-- SELECT count(*) FROM public.item WHERE is_active;
-- SELECT count(*) FROM public.item WHERE NOT is_active;
-- SELECT MIN(timestamp) FROM item;
-- SELECT count(*) FROM public.item WHERE timestamp > '2021-03-12';
-- SELECT store_id, store.name, count(*) AS total FROM public.item INNER JOIN public.store ON store.id = store_id WHERE timestamp > '2021-03-12' GROUP BY store.name, store_id ORDER BY total;
-- SELECT MAX(timestamp) AS timestamp, store_id FROM item GROUP BY store_id ORDER BY timestamp DESC;