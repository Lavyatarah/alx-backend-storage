-- SQL script that creates a table users
SELECT
    origin,
    SUM(fans) AS nb_fans
FROM
    metal_bands
GROUP BY
    origin
ORDER BY
    nb_fans DESC;
