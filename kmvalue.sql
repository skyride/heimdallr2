SELECT core_killmail.id, SUM(core_item.quantity * sde_type.sell) + ship_type.sell AS value
FROM core_killmail
INNER JOIN core_item ON core_item.kill_id=core_killmail.id
INNER JOIN sde_type ON sde_type.id=core_item.type_id
INNER JOIN sde_type as ship_type on ship_type.id=core_killmail.ship_id
GROUP BY core_killmail.id
LIMIT 1000